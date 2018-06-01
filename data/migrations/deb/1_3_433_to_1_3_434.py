#!/usr/bin/python3.5
import os
import sys
import traceback

from indy_common.config_util import getConfig
from indy_common.config_helper import NodeConfigHelper

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.genesis_txn.genesis_txn_initiator_from_file import GenesisTxnInitiatorFromFile

from plenum.common.stack_manager import TxnStackManager
from plenum.common.ledger import Ledger
from stp_core.common.log import getlogger
from storage.helper import initHashStore

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"


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


def append_ips_to_env(node_ip):
    node_ip_key = 'NODE_IP'
    client_ip_key = 'NODE_CLIENT_IP'
    with open(ENV_FILE_PATH, "a") as fenv:
        fenv.write("\n{}={}\n".format(node_ip_key, node_ip))
        fenv.write("{}={}\n".format(client_ip_key, "0.0.0.0"))


def get_pool_ledger(node_name):
    config = getConfig()
    config_helper = NodeConfigHelper(node_name, config)

    genesis_txn_initiator = GenesisTxnInitiatorFromFile(config_helper.genesis_dir,
                                                        config.poolTransactionsFile)
    hash_store = initHashStore(config_helper.ledger_dir, "pool", config)
    return Ledger(CompactMerkleTree(hashStore=hash_store),
                  dataDir=config_helper.ledger_dir,
                  fileName=config.poolTransactionsFile,
                  ensureDurability=config.EnsureLedgerDurability,
                  genesis_txn_initiator=genesis_txn_initiator)


def migrate_all():
    node_name = get_node_name()
    if node_name is None:
        logger.error("Could not get node name")
        return False

    ledger = get_pool_ledger(node_name)
    nodeReg, _, _ = TxnStackManager.parseLedgerForHaAndKeys(ledger)

    if nodeReg is None:
        logger.error("Empty node registry returned by stack manager")
        return False

    if node_name not in nodeReg:
        logger.error("Node registry does not contain node {}".format(node_name))
        return False

    ha = nodeReg[node_name]
    if ha is None:
        logger.error("Empty HA for node {}".format(node_name))
        return False

    logger.info("HA for {}: {}".format(node_name, ha))

    try:
        append_ips_to_env(ha.host)
    except Exception:
        logger.error(traceback.print_exc())
        logger.error("Could not append node and client IPs to indy env file")
        return False

    return True


if migrate_all():
    logger.info("Migration complete: node and client IPs have been added to indy env file")
else:
    logger.error("Migration failed: node and client IPs have not been added to indy env file")
    sys.exit(1)
