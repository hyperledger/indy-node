#!/usr/bin/python3.5
import os
import shutil
import glob

from stp_core.common.log import getlogger
from sovrin_common.config_util import getConfig

config = getConfig()
logger = getlogger()

old_base_dir = '~/.indy'

def migrate_genesis_txn(old_base_txn_dir, new_base_txn_dir):
    for suffix in ('sandbox', 'live', 'local'):
        old_domain_genesis = os.path.join(
            old_base_txn_dir, 'domain_transactions_{}_genesis'.format(suffix))
        old_pool_genesis = os.path.join(
            old_base_txn_dir, 'pool_transactions_{}_genesis'.format(suffix))

        if os.path.exists(old_domain_genesis):
            shutil.move(old_domain_genesis, new_base_txn_dir)
        if os.path.exists(old_pool_genesis):
            shutil.move(old_pool_genesis, new_base_txn_dir)


def migrate_keys(old_base_keys_dir, new_base_keys_dir)
    for prefix in ('private', 'public', 'sig', 'verif'):
        old_keys_dir = os.path.join(old_base_keys_dir, '{}_keys'.format(prefix))
        if os.path.exists(old_keys_dir) and os.path.isdir(old_keys_dir):
            shutil.move(old_keys_dir, new_base_keys_dir)


def migrate_all():
    base_dir = config.baseDir

    old_node_base_data_dir = os.path.join(old_base_dir, 'data')
    old_nodes_data_dir = os.path.join(old_node_base_data_dir, 'nodes')
    old_wallets_dir = os.path.join(old_base_dir, 'wallets')
    old_general_config = os.path.join(old_base_dir, 'indy_config.py')
    old_daemon_config_base_dir = '/home/indy/.indy'
    old_daemon_config = os.path.join(old_daemon_config_base_dir, 'indy.env')

    new_log_dir = os.path.join(config.LOG_DIR, config.NETWORK_NAME)
    new_node_base_dir = os.path.join(base_dir , config.NETWORK_NAME)
    new_node_base_data_dir = os.path.join(config.NODE_BASE_DATA_DIR, config.NETWORK_NAME)

    new_general_config = os.path.join(config.GENERAL_CONFIG_DIR, config.GENERAL_CONFIG_FILE)

    # Move general config file
    os.rename(old_general_config, new_general_config)

    # Move genesis transactions
    migrate_genesis_txn(old_base_dir, new_node_base_dir)

    for node_name in os.listdir(old_nodes_data_dir):
        # Move logs
        old_node_logs_exp = os.path.join(old_base_dir, '{}.log*'.format(node_name))
        for node_log in glob.glob(old_node_logs_exp):
            shutil.move(node_log, new_log_dir)

        # Move keys
        old_keys_dir = os.path.join(old_base_dir, node_name)
        new_keys_dir = os.path.join(new_node_base_dir, node_name)
        os.mkdir(new_keys_dir)
        migrate_keys(old_keys_dir, new_keys_dir)

    # Move nodes data directory
    shutil.move(old_nodes_data_dir, new_node_base_data_dir)

    # Move wallets directory
    shutil.move(old_wallets_dir, new_node_base_dir)

    # Move daemon config
    shutil.move(old_daemon_config, config.GENERAL_CONFIG_DIR)


if os.path.exists(old_base_dir):
    migrate_all()
