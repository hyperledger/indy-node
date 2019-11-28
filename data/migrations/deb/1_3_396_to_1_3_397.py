#!/usr/bin/python3.5
import os
import sys
import shutil
import traceback
import tarfile
import pwd
import grp
import stat

from stp_core.common.log import getlogger
from storage.kv_store_leveldb import KeyValueStorageLeveldb
from storage.kv_store_rocksdb import KeyValueStorageRocksdb
from storage.kv_store_leveldb_int_keys import KeyValueStorageLeveldbIntKeys
from storage.kv_store_rocksdb_int_keys import KeyValueStorageRocksdbIntKeys

from indy_common.config_util import getConfig
from indy_common.config_helper import NodeConfigHelper


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


def archive_leveldb_ledger(node_name, leveldb_ledger_dir):
    leveldb_ledger_archive_name = node_name + "_ledger_leveldb.tar.gz"
    leveldb_ledger_archive_path = os.path.join("/tmp", leveldb_ledger_archive_name)
    tar = tarfile.open(leveldb_ledger_archive_path, "w:gz")
    tar.add(leveldb_ledger_dir, arcname=node_name)
    tar.close()
    logger.info("Archive of LevelDB-based ledger created: {}"
                .format(leveldb_ledger_archive_path))


def migrate_storage(level_db_dir, rocks_db_dir, db_name, is_db_int_keys):
    if is_db_int_keys is True:
        KeyValueStorageLeveldbCls = KeyValueStorageLeveldbIntKeys
        KeyValueStorageRocksdbCls = KeyValueStorageRocksdbIntKeys
    else:
        KeyValueStorageLeveldbCls = KeyValueStorageLeveldb
        KeyValueStorageRocksdbCls = KeyValueStorageRocksdb

    try:
        leveldb_storage = KeyValueStorageLeveldbCls(level_db_dir, db_name, read_only=True)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not open leveldb storage: {}".format(os.path.join(level_db_dir, db_name)))
        return False

    try:
        rocksdb_storage = KeyValueStorageRocksdbCls(rocks_db_dir, db_name)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not open rocksdb storage: {}".format(os.path.join(rocks_db_dir, db_name)))
        return False

    try:
        for key, val in leveldb_storage.iterator():
            rocksdb_storage.put(bytes(key), bytes(val))
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not put key/value to RocksDB storage '{}'".format(db_name))
        return False

    leveldb_storage.close()
    rocksdb_storage.close()

    return True


def migrate_storages(leveldb_ledger_dir, rocksdb_ledger_dir):
    # Migrate transaction logs, they use integer keys
    for ledger_type in ledger_types:
        db_name = ledger_type + "_transactions"
        if not migrate_storage(leveldb_ledger_dir, rocksdb_ledger_dir, db_name, True):
            logger.error("Could not migrate {}, DB path: {}"
                         .format(db_name, os.path.join(leveldb_ledger_dir, db_name)))
            return False

    # Migrate other storages with non-integer keys
    for db_name in ["attr_db", "idr_cache_db", "seq_no_db", "state_signature"]:
        if not migrate_storage(leveldb_ledger_dir, rocksdb_ledger_dir, db_name, False):
            logger.error("Could not migrate {}, DB path: {}"
                         .format(db_name, os.path.join(leveldb_ledger_dir, db_name)))
            return False

    return True


def migrate_all():
    node_name = get_node_name()
    if node_name is None:
        logger.error("Could not get node name")
        return False

    config = getConfig()
    config_helper = NodeConfigHelper(node_name, config)

    leveldb_ledger_dir = config_helper.ledger_dir
    rocksdb_ledger_dir = os.path.join(config_helper.ledger_data_dir, node_name + "_rocksdb")
    if os.path.exists(rocksdb_ledger_dir):
        logger.error("Temporary directory for RocksDB-based ledger exists, please remove: {}"
                     .format(rocksdb_ledger_dir))
        return False

    try:
        os.mkdir(rocksdb_ledger_dir)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not create temporary directory for RocksDB-based ledger: {}"
                     .format(rocksdb_ledger_dir))
        return False

    logger.info("Starting migration of storages from LevelDB to RocksDB...")

    if migrate_storages(leveldb_ledger_dir, rocksdb_ledger_dir):
        logger.info("All storages migrated successfully from LevelDB to RocksDB")
    else:
        logger.error("Storages migration from LevelDB to RocksDB failed!")
        shutil.rmtree(rocksdb_ledger_dir)
        return False

    # Archiving LevelDB-based ledger
    try:
        archive_leveldb_ledger(node_name, leveldb_ledger_dir)
    except Exception:
        logger.warning("Could not create an archive of LevelDB-based ledger, proceed anyway")

    # TODO: it whould be nice to open new RocksDB-based ledger
    # and compare root hashes with LevelDB-based ledger here

    # Remove LevelDB-based ledger
    try:
        shutil.rmtree(leveldb_ledger_dir)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not remove LevelDB-based ledger: {}"
                     .format(leveldb_ledger_dir))
        shutil.rmtree(rocksdb_ledger_dir)
        return False

    ledger_dir = leveldb_ledger_dir

    try:
        shutil.move(rocksdb_ledger_dir, ledger_dir)
    except Exception:
        logger.error(traceback.format_exc())
        logger.error("Could not rename temporary RocksDB-based ledger from '{}' to '{}'"
                     .format(rocksdb_ledger_dir, ledger_dir))
        shutil.rmtree(rocksdb_ledger_dir)
        return False

    set_own_perm("indy", ledger_dir)

    return True


if migrate_all():
    logger.info("Migration from LevelDB to RocksDB complete")
else:
    logger.info("Migration from LevelDB to RocksDB failed!")
    sys.exit(1)
