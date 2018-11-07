#!/usr/bin/python3.5
import json
import os
import shutil
import subprocess

from common.serializers.compact_serializer import CompactSerializer
from common.serializers.json_serializer import JsonSerializer
from common.serializers.mapping_serializer import MappingSerializer
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from plenum.common.constants import TXN_TYPE, DATA
from plenum.persistence.leveldb_hash_store import LevelDbHashStore
from storage import store_utils
from storage.chunked_file_store import ChunkedFileStore
from stp_core.common.log import getlogger

from indy_common.config_util import getConfig
from indy_common.constants import SCHEMA, CLAIM_DEF
from indy_common.txn_util import getTxnOrderedFields

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

    # open the current ledger using the specified serializer
    old_txn_log_store = ChunkedFileStore(data_directory,
                                         old_ledger_file,
                                         isLineNoKey=True,
                                         storeContentHash=False)
    logger.info("Old ledger folder: {}, {}".format(
        data_directory, old_ledger_file))
    old_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        txn_serializer=serializer,
                        hash_serializer=serializer,
                        fileName=old_ledger_file,
                        transactionLogStore=old_txn_log_store)
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
        if txn[TXN_TYPE] == SCHEMA:
            if DATA in txn:
                txn[DATA] = json.loads(txn[DATA])
        if txn[TXN_TYPE] == CLAIM_DEF:
            if DATA in txn:
                txn[DATA] = json.loads(txn[DATA])
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


def migrate_all_hash_stores(node_data_directory):
    # the new hash store (merkle tree) will be recovered from the new transaction log after re-start
    # just delete the current hash store
    old_merkle_nodes = os.path.join(node_data_directory, '_merkleNodes')
    old_merkle_leaves = os.path.join(node_data_directory, '_merkleLeaves')
    old_merkle_nodes_bin = os.path.join(
        node_data_directory, '_merkleNodes.bin')
    old_merkle_leaves_bin = os.path.join(
        node_data_directory, '_merkleLeaves.bin')
    old_merkle_nodes_config_bin = os.path.join(
        node_data_directory, 'config_merkleNodes.bin')
    old_merkle_leaves_config_bin = os.path.join(
        node_data_directory, 'config_merkleLeaves.bin')

    if os.path.exists(old_merkle_nodes):
        shutil.rmtree(old_merkle_nodes)
    if os.path.exists(old_merkle_leaves):
        shutil.rmtree(old_merkle_leaves)
    if os.path.exists(old_merkle_nodes_bin):
        os.remove(old_merkle_nodes_bin)
    if os.path.exists(old_merkle_leaves_bin):
        os.remove(old_merkle_leaves_bin)
    if os.path.exists(old_merkle_nodes_config_bin):
        os.remove(old_merkle_nodes_config_bin)
    if os.path.exists(old_merkle_leaves_config_bin):
        os.remove(old_merkle_leaves_config_bin)

    # open new Ledgers
    _open_new_ledger(node_data_directory, config.poolTransactionsFile, 'pool')
    _open_new_ledger(node_data_directory,
                     config.domainTransactionsFile, 'domain')
    _open_new_ledger(node_data_directory,
                     config.configTransactionsFile, 'config')


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

        if os.path.exists(new_domain_genesis):
            os.remove(new_domain_genesis)
        if os.path.exists(new_pool_genesis):
            os.remove(new_pool_genesis)

        if os.path.exists(old_domain_genesis):
            old_ser = CompactSerializer(getTxnOrderedFields())
            new_ser = JsonSerializer()
            with open(old_domain_genesis, 'r') as f1:
                with open(new_domain_genesis, 'w') as f2:
                    for line in store_utils.cleanLines(f1):
                        txn = old_ser.deserialize(line)
                        txn = {k: v for k, v in txn.items() if v}
                        txn = new_ser.serialize(txn, toBytes=False)
                        f2.write(txn)
                        f2.write('\n')
            os.remove(old_domain_genesis)
        if os.path.exists(old_pool_genesis):
            os.rename(old_pool_genesis, new_pool_genesis)


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
        logger.info("Applying migration to {}".format(node_data_dir))
        migrate_all_ledgers_for_node(node_data_dir)
        migrate_all_hash_stores(node_data_dir)
        migrate_all_states(node_data_dir)

    migrate_genesis_txn(base_dir)


migrate_all()
