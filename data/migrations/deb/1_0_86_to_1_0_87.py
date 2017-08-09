#!/usr/bin/python3.5
import os
import shutil

from common.serializers.compact_serializer import CompactSerializer
from common.serializers.json_serializer import JsonSerializer
from common.serializers.mapping_serializer import MappingSerializer
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from plenum.persistence.leveldb_hash_store import LevelDbHashStore
from storage.chunked_file_store import ChunkedFileStore

from sovrin_common.config_util import getConfig
from sovrin_common.txn_util import getTxnOrderedFields


def migrate_ledger(data_directory,
                   old_ledger_file, new_ledger_file,
                   serializer: MappingSerializer = None):
    """
    Test for the directory, open old and new ledger, migrate data, rename directories
    """

    # we should have ChunkedFileStorage implementation of the Ledger
    if not os.path.isdir(os.path.join(data_directory, old_ledger_file)):
        print("Could not find directory {} for migration.".format(old_ledger_file))
        return

    # open the current ledger using the specified serializer
    old_txn_log_store = ChunkedFileStore(data_directory,
                                         old_ledger_file,
                                         isLineNoKey=True,
                                         storeContentHash=False)
    old_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        txn_serializer=serializer,
                        hash_serializer=serializer,
                        fileName=old_ledger_file,
                        transactionLogStore=old_txn_log_store)
    print("old size for {}: {}".format(old_ledger_file, str(old_ledger.size)))

    # open the new ledger with new serialization
    new_ledger_file_backup = new_ledger_file + "_new"
    new_ledger = Ledger(CompactMerkleTree(),
                        dataDir=data_directory,
                        fileName=new_ledger_file_backup)

    # add all txns into the new ledger
    for _, txn in old_ledger.getAllTxn():
        new_ledger.add(txn)
    print("new size for {}: {}".format(new_ledger_file, str(new_ledger.size)))

    old_ledger.stop()
    new_ledger.stop()

    # now that everything succeeded, remove the old files and move the new files into place
    shutil.rmtree(
        os.path.join(data_directory, old_ledger_file))
    os.rename(
        os.path.join(data_directory, new_ledger_file_backup),
        os.path.join(data_directory, new_ledger_file))


def open_new_ledger(data_directory, new_ledger_file, hash_store_name):
    # open new Ledger with leveldb hast store (to re-init it)
    new_ledger = Ledger(CompactMerkleTree(
        hashStore=LevelDbHashStore(
            dataDir=data_directory, fileNamePrefix=hash_store_name)),
        dataDir=data_directory,
        fileName=new_ledger_file)
    new_ledger.stop()


def migrate_all_hash_stores(data_directory):
    # the new hash store (merkle tree) will be recovered from the new transaction log after re-start
    # just delete the current hash store
    shutil.rmtree(
        os.path.join(data_directory, '_merkleNodes'))
    shutil.rmtree(
        os.path.join(data_directory, '_merkleLeaves'))
    os.remove(
        os.path.join(data_directory, '_merkleNodes.bin'))
    os.remove(
        os.path.join(data_directory, '_merkleLeaves.bin'))
    os.remove(
        os.path.join(data_directory, 'config_merkleNodes.bin'))
    os.remove(
        os.path.join(data_directory, 'config_merkleLeaves.bin'))

    # open new Ledgers
    open_new_ledger(data_directory, config.poolTransactionsFile, 'pool')
    open_new_ledger(data_directory, config.domainTransactionsFile, 'domain')
    open_new_ledger(data_directory, config.configTransactionsFile, 'config')


def migrate_all_ledgers_for_node(node_data_directory):
    # using default ledger names
    migrate_ledger(node_data_directory,
                   config.poolTransactionsFile, config.poolTransactionsFile,
                   serializer=JsonSerializer())
    migrate_ledger(node_data_directory,
                   config.configTransactionsFile, config.configTransactionsFile,
                   serializer=JsonSerializer())

    # domain ledger uses custom CompactSerializer and old file name
    fields = getTxnOrderedFields()
    migrate_ledger(node_data_directory,
                   config.domainTransactionsFile.replace('domain_', ''), config.domainTransactionsFile,
                   serializer=CompactSerializer(fields=fields))


if __name__ == "__main__":
    config = getConfig()
    base_dir = config.baseDir
    nodes_data_dir = os.path.join(base_dir, config.nodeDataDir)
    for node_dir in os.listdir(nodes_data_dir):
        node_data_dir = os.path.join(nodes_data_dir, node_dir)
        migrate_all_ledgers_for_node(node_data_dir)
        migrate_all_hash_stores(node_data_dir)
