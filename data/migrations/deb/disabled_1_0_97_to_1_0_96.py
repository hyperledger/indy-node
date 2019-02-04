#!/usr/bin/python3.5
import os
import shutil

import subprocess
from common.serializers.compact_serializer import CompactSerializer
from common.serializers.json_serializer import JsonSerializer
from common.serializers.mapping_serializer import MappingSerializer
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from plenum.persistence.leveldb_hash_store import LevelDbHashStore
from storage import store_utils
from storage.chunked_file_store import ChunkedFileStore

from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
from stp_core.common.log import getlogger

config = getConfig()
logger = getlogger()


def _migrate_ledger(data_directory,
                    old_ledger_file, new_ledger_file,
                    serializer: MappingSerializer = None):
    """
    Test for the directory, open old and new ledger, migrate data, rename directories
    """

    # we should have ChunkedFileStorage implementation of the Ledger
    if not os.path.isdir(os.path.join(data_directory, old_ledger_file)):
        msg = 'Could not find directory {} for migration.'.format(
            old_ledger_file)
        logger.error(msg)
        raise Exception(msg)

    # open the old ledger using the specified serializer
    old_ledger_file_backup = old_ledger_file + "_new"
    old_txn_log_store = ChunkedFileStore(data_directory,
                                         old_ledger_file_backup,
                                         isLineNoKey=True,
                                         storeContentHash=False)
    old_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        txn_serializer=serializer,
                        hash_serializer=serializer,
                        fileName=old_ledger_file_backup,
                        transactionLogStore=old_txn_log_store)

    # open the new ledger with new serialization
    new_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        fileName=new_ledger_file)
    logger.info("new size for {}: {}".format(
        old_ledger_file_backup, str(new_ledger.size)))

    # add all txns into the old ledger
    for _, txn in new_ledger.getAllTxn():
        old_ledger.add(txn)
    logger.info("old size for {}: {}".format(
        new_ledger_file, str(old_ledger.size)))

    old_ledger.stop()
    new_ledger.stop()

    # now that everything succeeded, remove the new files and move the old
    # files into place
    shutil.rmtree(
        os.path.join(data_directory, new_ledger_file))
    os.rename(
        os.path.join(data_directory, old_ledger_file_backup),
        os.path.join(data_directory, old_ledger_file))


def _open_old_ledger(data_directory, old_ledger_file,
                     hash_store_name, serializer):
    # open old Ledger with leveldb hash store (to re-init it)
    old_txn_log_store = ChunkedFileStore(data_directory,
                                         old_ledger_file,
                                         isLineNoKey=True,
                                         storeContentHash=False)
    old_ledger = Ledger(CompactMerkleTree(
        hashStore=LevelDbHashStore(
            dataDir=data_directory,
            fileNamePrefix=hash_store_name)),
        dataDir=data_directory,
        txn_serializer=serializer,
        hash_serializer=serializer,
        fileName=old_ledger_file,
        transactionLogStore=old_txn_log_store)

    old_ledger.stop()


def migrate_all_hash_stores(node_data_directory):
    # the new hash store (merkle tree) will be recovered from the new transaction log after re-start
    # just delete the current hash store
    new_merkle_nodes = os.path.join(node_data_directory, '_merkleNodes')
    new_merkle_leaves = os.path.join(node_data_directory, '_merkleLeaves')
    new_merkle_nodes_bin = os.path.join(
        node_data_directory, '_merkleNodes.bin')
    new_merkle_leaves_bin = os.path.join(
        node_data_directory, '_merkleLeaves.bin')
    new_merkle_nodes_config_bin = os.path.join(
        node_data_directory, 'config_merkleNodes.bin')
    new_merkle_leaves_config_bin = os.path.join(
        node_data_directory, 'config_merkleLeaves.bin')

    if os.path.exists(new_merkle_nodes):
        shutil.rmtree(new_merkle_nodes)
    if os.path.exists(new_merkle_leaves):
        shutil.rmtree(new_merkle_leaves)
    if os.path.exists(new_merkle_nodes_bin):
        os.remove(new_merkle_nodes_bin)
    if os.path.exists(new_merkle_leaves_bin):
        os.remove(new_merkle_leaves_bin)
    if os.path.exists(new_merkle_nodes_config_bin):
        os.remove(new_merkle_nodes_config_bin)
    if os.path.exists(new_merkle_leaves_config_bin):
        os.remove(new_merkle_leaves_config_bin)

    # open new Ledgers
    fields = getTxnOrderedFields()
    _open_old_ledger(node_data_directory, config.poolTransactionsFile,
                     'pool', serializer=JsonSerializer())
    _open_old_ledger(node_data_directory, config.domainTransactionsFile,
                     'domain', serializer=CompactSerializer(fields=fields))
    _open_old_ledger(node_data_directory, config.configTransactionsFile,
                     'config', serializer=JsonSerializer())


def migrate_all_ledgers_for_node(node_data_directory):
    # using default ledger names
    _migrate_ledger(node_data_directory,
                    config.poolTransactionsFile, config.poolTransactionsFile,
                    serializer=JsonSerializer())
    _migrate_ledger(
        node_data_directory,
        config.configTransactionsFile,
        config.configTransactionsFile,
        serializer=JsonSerializer())

    # domain ledger uses custom CompactSerializer and old file name
    fields = getTxnOrderedFields()
    _migrate_ledger(node_data_directory,
                    config.domainTransactionsFile.replace(
                        'domain_', ''), config.domainTransactionsFile,
                    serializer=CompactSerializer(fields=fields))


def migrate_all_states(node_data_directory):
    # the states will be recovered from the ledger during the start-up.
    # just delete the current ones
    shutil.rmtree(
        os.path.join(node_data_directory, 'pool_state'))
    shutil.rmtree(
        os.path.join(node_data_directory, 'domain_state'))
    shutil.rmtree(
        os.path.join(node_data_directory, 'config_state'))


def migrate_genesis_txn(base_dir):
    for suffix in ('sandbox', 'live', 'local'):
        old_domain_genesis = os.path.join(
            base_dir, 'transactions_{}'.format(suffix))
        old_pool_genesis = os.path.join(
            base_dir, 'pool_transactions_{}'.format(suffix))

        new_domain_genesis = os.path.join(
            base_dir, 'domain_transactions_{}_genesis'.format(suffix))
        new_pool_genesis = os.path.join(
            base_dir, 'pool_transactions_{}_genesis'.format(suffix))

        if os.path.exists(old_domain_genesis):
            os.remove(old_domain_genesis)
        if os.path.exists(old_pool_genesis):
            os.remove(old_pool_genesis)

        if os.path.exists(new_domain_genesis):
            old_ser = CompactSerializer(getTxnOrderedFields())
            new_ser = JsonSerializer()
            with open(new_domain_genesis, 'r') as f1:
                with open(old_domain_genesis, 'w') as f2:
                    for line in store_utils.cleanLines(f1):
                        txn = new_ser.deserialize(line)
                        txn = old_ser.serialize(txn)
                        f2.write(txn)
            os.remove(new_domain_genesis)
        if os.path.exists(new_pool_genesis):
            os.rename(new_pool_genesis, old_domain_genesis)


def migrate_all():
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
        migrate_all_ledgers_for_node(node_data_dir)
        migrate_all_hash_stores(node_data_dir)
        migrate_all_states(node_data_dir)

    migrate_genesis_txn(base_dir)
    subprocess.run(['chown', '-R', 'sovrin:sovrin', '/home/sovrin/.sovrin'])


migrate_all()
