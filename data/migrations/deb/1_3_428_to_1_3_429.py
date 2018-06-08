#!/usr/bin/python3.5
import grp
import os
import pwd
import shutil
import stat
import sys
import tarfile
import traceback
import copy
from _sha256 import sha256

from common.serializers.serialization import ledger_txn_serializer, serialize_msg_for_signing
from indy_common.config_helper import NodeConfigHelper
from indy_common.config_util import getConfig
from indy_common.constants import CONFIG_LEDGER_ID
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.server.domain_req_handler import DomainReqHandler
from indy_node.server.pool_req_handler import PoolRequestHandler
from plenum.common.constants import TXN_TYPE, TXN_PAYLOAD, \
    TXN_PAYLOAD_METADATA, TXN_PAYLOAD_METADATA_DIGEST, POOL_LEDGER_ID, DOMAIN_LEDGER_ID
from plenum.common.txn_util import transform_to_new_format, get_from, get_req_id, get_payload_data, \
    get_protocol_version, get_seq_no, get_type
from plenum.common.types import f, OPERATION
from plenum.persistence.req_id_to_txn import ReqIdrToTxn
from storage.helper import initKeyValueStorage
from storage.kv_store_rocksdb_int_keys import KeyValueStorageRocksdbIntKeys
from stp_core.common.log import getlogger

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"
ledger_types = ['pool', 'domain', 'config']
config = getConfig()


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


def get_ledger_id_by_txn_type(txn_type):

    def get_types_for_req_handler(req_handler):
        return list(req_handler.write_types) + list(req_handler.query_types)

    if txn_type in get_types_for_req_handler(PoolRequestHandler):
        return POOL_LEDGER_ID
    elif txn_type in get_types_for_req_handler(DomainReqHandler):
        return DOMAIN_LEDGER_ID
    elif txn_type in get_types_for_req_handler(ConfigReqHandler):
        return CONFIG_LEDGER_ID
    else:
        logger.error("Unknown txn_type: {}".format(txn_type))
        logger.error("Cannot write txn into SeqNoDB, because cannot define ledger_id")
        sys.exit(1)


def migrate_txn_log(db_dir, db_name):

    def put_into_seq_no_db(txn):
        # If there is no reqId, then it's genesis txn
        if get_req_id(txn) is None:
            return
        txn_new = copy.deepcopy(txn)
        operation = get_payload_data(txn_new)
        operation[TXN_TYPE] = get_type(txn_new)
        dct = {
            f.IDENTIFIER.nm: get_from(txn_new),
            f.REQ_ID.nm: get_req_id(txn_new),
            OPERATION: operation,
        }
        if get_protocol_version(txn_new) is not None:
            dct[f.PROTOCOL_VERSION.nm] = get_protocol_version(txn_new)
        digest = sha256(serialize_msg_for_signing(dct)).hexdigest()
        seq_no = get_seq_no(txn_new)
        ledger_id = get_ledger_id_by_txn_type(operation[TXN_TYPE])
        line_to_record = str(ledger_id) + ReqIdrToTxn.delimiter + str(seq_no)
        dest_seq_no_db_storage.put(digest, line_to_record)
        return digest

    new_db_name = db_name + '_new'
    old_path = os.path.join(db_dir, db_name)
    new_path = os.path.join(db_dir, new_db_name)
    new_seqno_db_name = config.seqNoDbName + '_new'
    try:
        dest_seq_no_db_storage = initKeyValueStorage(config.reqIdToTxnStorage,
                                                     db_dir,
                                                     new_seqno_db_name)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not open new seq_no_db storage")
        return False

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
            key = key.decode()
            val = ledger_txn_serializer.deserialize(val)
            new_val = transform_to_new_format(txn=val, seq_no=int(key))
            digest = put_into_seq_no_db(new_val)
            # add digest into txn
            if get_req_id(new_val):
                new_val[TXN_PAYLOAD][TXN_PAYLOAD_METADATA][TXN_PAYLOAD_METADATA_DIGEST] = digest
            new_val = ledger_txn_serializer.serialize(new_val)
            dest_storage.put(key, new_val)

    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not put key/value to the new ledger '{}'".format(db_name))
        return False

    src_storage.close()
    dest_storage.close()
    dest_seq_no_db_storage.close()

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
    try:
        set_own_perm("indy", old_path)
    except Exception:
        pass

    return True


def rename_seq_no_db(db_dir):
    old_seqno_path = os.path.join(db_dir, config.seqNoDbName)
    new_seqno_db_name = config.seqNoDbName + '_new'
    new_seqno_path = os.path.join(db_dir, new_seqno_db_name)
    try:
        shutil.move(new_seqno_path, old_seqno_path)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not rename temporary new seq_no_db from '{}' to '{}'"
                     .format(new_seqno_path, old_seqno_path))
        return False

    set_own_perm("indy", old_seqno_path)


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


def migrate_ts_store(ledger_dir):
    # just remove, since state root hash may be changed
    for ledger_type in ledger_types:
        db = os.path.join(ledger_dir, config.stateTsDbName)
        if os.path.exists(db):
            shutil.rmtree(db)
    return True


def migrate_bls_signature_store(ledger_dir):
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

    # Rename new seq_no_db into old
    rename_seq_no_db(ledger_dir)

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
    if migrate_ts_store(ledger_dir):
        logger.info("Timestamp store migrated successfully from old to new transaction format")
    else:
        logger.error("Timestamp store migration from old to new format failed!")
        return False

    # 6. migrate bls signature xtore
    if migrate_bls_signature_store(ledger_dir):
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
