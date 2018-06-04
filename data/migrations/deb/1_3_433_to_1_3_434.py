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

node_name_key = 'NODE_NAME'
node_ip_key = 'NODE_IP'
client_ip_key = 'NODE_CLIENT_IP'


def get_node_name():
    node_name = None

    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as fenv:
            for line in fenv.readlines():
                if line.find(node_name_key) != -1:
                    node_name = line.split('=')[1].strip()
                    break
    else:
        logger.error("Path to env file does not exist")

    return node_name


def are_ips_present_in_env():
    node_ip_present = False
    client_ip_present = False

    with open(ENV_FILE_PATH, "r") as fenv:
        for line in fenv.readlines():
            key = line.split('=')[0].strip()
            if key == node_ip_key:
                node_ip_present = True
                logger.info("Node IP is present in '{}': {}".format(ENV_FILE_PATH, line.strip()))
            elif key == client_ip_key:
                client_ip_present = True
                logger.info("Client IP is present in '{}': {}".format(ENV_FILE_PATH, line.strip()))
    return node_ip_present, client_ip_present


def append_ips_to_env(node_ip, client_ip):
    node_ip_key = 'NODE_IP'
    client_ip_key = 'NODE_CLIENT_IP'

    if node_ip is None and client_ip is None:
        return

    with open(ENV_FILE_PATH, "a") as fenv:
        fenv.write("\n")
        if node_ip is not None:
            line = node_ip_key + "=" + node_ip
            logger.info("Appending line to '{}': {}".format(ENV_FILE_PATH, line))
            fenv.write("{}\n".format(line))
        if client_ip is not None:
            line = client_ip_key + "=" + client_ip
            logger.info("Appending line to '{}': {}".format(ENV_FILE_PATH, line))
            fenv.write("{}\n".format(line))


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


def get_node_ip():
    node_name = get_node_name()
    if node_name is None:
        raise RuntimeError("Could not get node name")

    ledger = get_pool_ledger(node_name)
    nodeReg, _, _ = TxnStackManager.parseLedgerForHaAndKeys(ledger)
    ledger.stop()

    if nodeReg is None:
        raise RuntimeError("Empty node registry returned by stack manager")

    if node_name not in nodeReg:
        raise ValueError("Node registry does not contain node {}".format(node_name))

    ha = nodeReg[node_name]
    if ha is None:
        raise ValueError("Empty HA for node {}".format(node_name))

    logger.info("HA for {}: {}".format(node_name, ha))

    return ha.host


def migrate_all():
    node_ip = None
    client_ip = None
    node_ip_present, client_ip_present = are_ips_present_in_env()

    if not node_ip_present:
        logger.info("Could not find {} in env file, try to get it from pool ledger".format(node_ip_key))

        try:
            node_ip = get_node_ip()
        except Exception:
            logger.error(traceback.print_exc())
            logger.error("Could not get node IP from pool ledger")
            return False

        logger.info("Got node ip from pool ledger: {}".format(node_ip))

    if not client_ip_present:
        client_ip = "0.0.0.0"

    if node_ip is not None or client_ip is not None:
        try:
            append_ips_to_env(node_ip, client_ip)
        except Exception:
            logger.error(traceback.print_exc())
            logger.error("Could not append node and client IPs to indy env file")
            return False
    else:
        logger.info("No modification of env file is needed")

    return True


if migrate_all():
    logger.info("Node/client IPs migration complete")
else:
    logger.error("Node/client IPs migration failed.")
    sys.exit(1)
