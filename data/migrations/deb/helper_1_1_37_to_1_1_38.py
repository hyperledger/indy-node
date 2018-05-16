#!/usr/bin/python3.5
import fileinput
import os
import shutil
import sys

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from plenum.persistence.leveldb_hash_store import LevelDbHashStore
from stp_core.common.log import getlogger

from sovrin_common.config_util import getConfig

logger = getlogger()


def _migrate_ledger(data_directory,
                    old_ledger_file, new_ledger_file):
    """
    Test for the directory, open old and new ledger, migrate data, rename directories
    """

    # open the current ledger
    logger.info("Old ledger folder: {}, {}".format(
        data_directory, old_ledger_file))
    old_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        fileName=old_ledger_file)
    logger.info("old size for {}: {}".format(
        old_ledger_file, str(old_ledger.size)))

    # open the new ledger with new serialization
    new_ledger_file_backup = new_ledger_file + "_new"
    logger.info("New ledger folder: {}, {}".format(
        data_directory, new_ledger_file_backup))
    new_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        fileName=new_ledger_file_backup)

    # add all txns into the new ledger
    for _, txn in old_ledger.getAllTxn():
        # remove all NULL values from there!
        txn = _prepare_old_txn(txn)
        print(txn)
        new_ledger.add(txn)
    logger.info("new size for {}: {}".format(
        new_ledger_file, str(new_ledger.size)))

    old_ledger.stop()
    new_ledger.stop()

    # now that everything succeeded, remove the old files and move the new
    # files into place
    shutil.rmtree(
        os.path.join(data_directory, old_ledger_file))
    os.rename(
        os.path.join(data_directory, new_ledger_file_backup),
        os.path.join(data_directory, new_ledger_file))

    logger.info("Final new ledger folder: {}".format(
        os.path.join(data_directory, new_ledger_file)))


def _prepare_old_txn(txn):
    return {k: v for k, v in txn.items() if v is not None}


def _open_new_ledger(data_directory, new_ledger_file, hash_store_name):
    # open new Ledger with leveldb hash store (to re-init it)
    logger.info("Open new ledger folder: {}".format(
        os.path.join(data_directory, new_ledger_file)))
    new_ledger = Ledger(CompactMerkleTree(
        hashStore=LevelDbHashStore(
            dataDir=data_directory, fileNamePrefix=hash_store_name)),
        dataDir=data_directory,
        fileName=new_ledger_file)
    new_ledger.stop()


def migrate_domain_hash_stores(node_data_directory):
    # the new hash store (merkle tree) will be recovered from the new transaction log after re-start
    # just delete the current hash store
    old_merkle_nodes = os.path.join(node_data_directory, '_merkleNodes')
    old_merkle_leaves = os.path.join(node_data_directory, '_merkleLeaves')
    new_merkle_leaves_domain = os.path.join(
        node_data_directory, 'domain_merkleLeaves')
    new_merkle_nodes_domain = os.path.join(
        node_data_directory, 'domain_merkleNodes')

    if os.path.exists(old_merkle_nodes):
        logger.info('removed {}'.format(old_merkle_nodes))
        shutil.rmtree(old_merkle_nodes)
    if os.path.exists(old_merkle_leaves):
        logger.info('removed {}'.format(old_merkle_leaves))
        shutil.rmtree(old_merkle_leaves)
    if os.path.exists(new_merkle_leaves_domain):
        logger.info('removed {}'.format(new_merkle_leaves_domain))
        shutil.rmtree(new_merkle_leaves_domain)
    if os.path.exists(new_merkle_nodes_domain):
        shutil.rmtree(new_merkle_nodes_domain)
        logger.info('removed {}'.format(new_merkle_nodes_domain))

    # open new Ledgers
    _, new_domain_ledger_name = _get_domain_ledger_file_names()
    _open_new_ledger(node_data_directory,
                     new_domain_ledger_name, 'domain')


def _get_domain_ledger_file_names():
    config = getConfig()
    if config.domainTransactionsFile.startswith('domain'):
        old_name = config.domainTransactionsFile
        new_name = config.domainTransactionsFile
    else:
        # domain ledger uses old file name
        old_name = config.domainTransactionsFile.replace('domain_', '')
        new_name = 'domain_' + config.domainTransactionsFile
        # new_name = old_name
    return old_name, new_name


def migrate_domain_ledger_for_node(node_data_directory):
    old_name, new_name = _get_domain_ledger_file_names()
    _migrate_ledger(node_data_directory,
                    old_name,
                    new_name)


def migrate_all_states(node_data_directory):
    # the states will be recovered from the ledger during the start-up.
    # just delete the current ones
    pool_state_path = os.path.join(node_data_directory, 'pool_state')
    domain_state_path = os.path.join(node_data_directory, 'domain_state')
    config_state_path = os.path.join(node_data_directory, 'config_state')

    if os.path.exists(pool_state_path):
        shutil.rmtree(pool_state_path)
        logger.info('removed {}'.format(pool_state_path))

    if os.path.exists(domain_state_path):
        shutil.rmtree(domain_state_path)
        logger.info('removed {}'.format(domain_state_path))

    if os.path.exists(config_state_path):
        shutil.rmtree(config_state_path)
        logger.info('removed {}'.format(config_state_path))


def migrate_custom_config(config_file):
    # config_file = os.path.join(node_data_directory, 'sovrin_config.py')
    if not os.path.exists(config_file):
        return

    logger.info("Migrating custom config file : {}".format(config_file))

    for line in fileinput.input(config_file, inplace=1):
        if 'domainTransactionsFile' in line:
            sys.stdout.write("domainTransactionsFile = 'domain_transactions_live'\n")
            continue
        sys.stdout.write(line)


def migrate_all():
    config = getConfig()
    base_dir = config.baseDir
    nodes_data_dir = os.path.join(base_dir, config.nodeDataDir)
    if not os.path.exists(nodes_data_dir):
        # TODO: find a better way
        base_dir = '/home/sovrin/.sovrin'
        nodes_data_dir = os.path.join(base_dir, config.nodeDataDir)
    if not os.path.exists(nodes_data_dir):
        msg = 'Can not find the directory with the ledger: {}'.format(
            nodes_data_dir)
        logger.error(msg)
        raise Exception(msg)

    for node_dir in os.listdir(nodes_data_dir):
        node_data_dir = os.path.join(nodes_data_dir, node_dir)
        logger.info("Applying migration to {}".format(node_data_dir))

        config_file = os.path.join(base_dir, 'sovrin_config.py')
        migrate_custom_config(config_file)

        migrate_domain_ledger_for_node(node_data_dir)
        migrate_domain_hash_stores(node_data_dir)
        migrate_all_states(node_data_dir)

        # subprocess.run(['chown', '-R', 'sovrin:sovrin', '/home/sovrin/.sovrin'])


migrate_all()
