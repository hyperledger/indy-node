#!/usr/bin/python3.5
import grp
import os
import pwd
import shutil
import stat
import sys
import tarfile
import traceback

from common.serializers.serialization import ledger_txn_serializer
from indy_common.config_helper import NodeConfigHelper
from indy_common.config_util import getConfig
from plenum.common.txn_util import transform_to_new_format
from storage.kv_store_rocksdb_int_keys import KeyValueStorageRocksdbIntKeys
from stp_core.common.log import getlogger

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"
ledger_types = ['pool', 'domain', 'config']


def set_own_perm(usr, dir):
    uid = pwd.getpwnam(usr).pw_uid
    gid = grp.getgrnam(usr).gr_gid
    perm_mask_rw = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
    perm_mask_rwx = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP

    os.chown(dir, uid, gid)
    os.chmod(dir, perm_mask_rwx)
    for croot, sub_dirs, cfiles in os.walk(dir):
        for fs_name in sub_dirs:
            os.chown(os.path.join(croot, fs_name), uid, gid)
            os.chmod(os.path.join(croot, fs_name), perm_mask_rwx)
        for fs_name in cfiles:
            os.chown(os.path.join(croot, fs_name), uid, gid)
            os.chmod(os.path.join(croot, fs_name), perm_mask_rw)


def get_node_name():
    node_name = None
    node_name_key = 'NODE_NAME'

    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as fenv:
            for line in fenv.readlines():
                if line.find(node_name_key) != -1:
                    node_name = line.split('=')[1].strip()
                    break
    else:
        logger.error("Path to env file does not exist")

    return node_name


def migrate_txn_log(db_dir, db_name):
    new_db_name = db_name + '_new'
    old_path = os.path.join(db_dir, db_name)
    new_path = os.path.join(db_dir, new_db_name)

    # open new and old ledgers
    try:
        src_storage = KeyValueStorageRocksdbIntKeys(db_dir, db_name, read_only=True)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not open old ledger: {}".format(os.path.join(db_dir, db_name)))
        return False

    try:
        dest_storage = KeyValueStorageRocksdbIntKeys(db_dir, new_db_name)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not open new ledger: {}".format(os.path.join(db_dir, new_db_name)))
        return False

    # put values from old ledger to the new one
    try:
        for key, val in src_storage.iterator():
            val = ledger_txn_serializer.deserialize(val)
            new_val = transform_to_new_format(txn=val, seq_no=key)
            new_val = ledger_txn_serializer.serialize(new_val)
            dest_storage.put(key, new_val)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not put key/value to the new ledger '{}'".format(db_name))
        return False

    src_storage.close()
    dest_storage.close()

    # Remove old ledger
    try:
        shutil.rmtree(old_path)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not remove old ledger: {}"
                     .format(old_path))
        return False

    # Rename new ledger to old one
    try:
        shutil.move(new_path, old_path)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not rename temporary new ledger from '{}' to '{}'"
                     .format(new_path, old_path))
        return False

    set_own_perm("indy", old_path)

    return True


def migrate_txn_logs(ledger_dir):
    # Migrate transaction logs, they use integer keys
    for ledger_type in ledger_types:
        db_name = ledger_type + "_transactions"
        if not migrate_txn_log(ledger_dir, db_name):
            logger.error("Could not migrate {}, DB path: {}"
                         .format(db_name, os.path.join(ledger_dir, db_name)))
            return False

    return True


def migrate_hash_stores(ledger_dir):
    for ledger_type in ledger_types:
        leaves_db = os.path.join(ledger_dir, ledger_type + '_merkleLeaves')
        nodes_db = os.path.join(ledger_dir, ledger_type + '_merkleNodes')
        if os.path.exists(leaves_db):
            shutil.rmtree(leaves_db)
        if os.path.exists(nodes_db):
            shutil.rmtree(nodes_db)
    return True


def migrate_states(ledger_dir):
    # just remove, it will be re-created from txn log
    for ledger_type in ledger_types:
        db = os.path.join(ledger_dir, ledger_type + '_state')
        if os.path.exists(db):
            shutil.rmtree(db)
    return True


def migrate_ts_store(ledger_dir, config):
    # just remove, since state root hash may be changed
    for ledger_type in ledger_types:
        db = os.path.join(ledger_dir, config.stateTsDbName)
        if os.path.exists(db):
            shutil.rmtree(db)
    return True


def migrate_bls_signature_store(ledger_dir, config):
    # just remove, since state root hash may be changed
    for ledger_type in ledger_types:
        db = os.path.join(ledger_dir, config.stateSignatureDbName)
        if os.path.exists(db):
            shutil.rmtree(db)
    return True


def archive_old_ledger(node_name, ledger_dir):
    ledger_archive_name = node_name + "_old_txn_ledger.tar.gz"
    ledger_archive_path = os.path.join("/tmp", ledger_archive_name)
    tar = tarfile.open(ledger_archive_path, "w:gz")
    tar.add(ledger_dir, arcname=node_name)
    tar.close()
    logger.info("Archive of old transaction format ledger created: {}"
                .format(ledger_archive_path))


def migrate_all():
    node_name = get_node_name()
    if node_name is None:
        logger.error("Could not get node name")
        return False

    config = getConfig()
    config_helper = NodeConfigHelper(node_name, config)

    ledger_dir = config_helper.ledger_dir

    # 1. Archiving old ledger
    try:
        archive_old_ledger(node_name, ledger_dir)
    except Exception:
        logger.warning("Could not create an archive of old transactions ledger, proceed anyway")

    # 2. migrate txn log
    if migrate_txn_logs(ledger_dir):
        logger.info("All txn logs migrated successfully from old to new transaction format")
    else:
        logger.error("Txn log migration from old to new format failed!")
        return False

    # 3. migrate hash store
    if migrate_hash_stores(ledger_dir):
        logger.info("All hash stores migrated successfully from old to new transaction format")
    else:
        logger.error("Hash store migration from old to new format failed!")
        return False

    # 4. migrate states
    if migrate_states(ledger_dir):
        logger.info("All states migrated successfully from old to new transaction format")
    else:
        logger.error("State migration from old to new format failed!")
        return False

    # 5. migrate ts store
    if migrate_ts_store(ledger_dir, config):
        logger.info("Timestamp store migrated successfully from old to new transaction format")
    else:
        logger.error("Timestamp store migration from old to new format failed!")
        return False

    # 6. migrate bls signature xtore
    if migrate_bls_signature_store(ledger_dir, config):
        logger.info("BLS signature store migrated successfully from old to new transaction format")
    else:
        logger.error("BLS signature store migration from old to new format failed!")
        return False

    return True


if migrate_all():
    logger.info("Migration of txns format")
else:
    logger.info("Migration of txns format failed!")
    sys.exit(1)
