#!/usr/bin/python3.5
import os
import shutil
import glob
from importlib.util import module_from_spec, spec_from_file_location

from stp_core.common.log import getlogger

baseDir = '/var/lib/indy'
GENERAL_CONFIG_DIR = '/etc/indy'
GENERAL_CONFIG_FILE = 'indy_config.py'
LOG_DIR = '/var/log/indy'
NODE_BASE_DATA_DIR = baseDir
CLI_BASE_DIR = '/home/indy/.indy-cli'
CLI_NETWORK_DIR = '/home/indy/.indy-cli/networks'

logger = getlogger()

old_base_dir = '/home/indy/.indy'


def migrate_genesis_txn(old_base_txn_dir, new_base_txn_dir):
    logger.info('Move genesis transactions {} -> {}'.format(
        old_base_txn_dir, new_base_txn_dir))
    for suffix in ('sandbox', 'live', 'local'):
        new_txn_dir = os.path.join(new_base_txn_dir, suffix)
        os.makedirs(new_txn_dir, exist_ok=True)

        old_domain_genesis = os.path.join(
            old_base_txn_dir, 'domain_transactions_{}_genesis'.format(suffix))
        old_pool_genesis = os.path.join(
            old_base_txn_dir, 'pool_transactions_{}_genesis'.format(suffix))
        new_domain_genesis = os.path.join(
            new_txn_dir, 'domain_transactions_genesis')
        new_pool_genesis = os.path.join(
            new_txn_dir, 'pool_transactions_genesis')

        if os.path.exists(old_domain_genesis):
            shutil.move(old_domain_genesis, new_domain_genesis)
        if os.path.exists(old_pool_genesis):
            shutil.move(old_pool_genesis, new_pool_genesis)

    logger.info('done')


def migrate_keys(old_base_keys_dir, new_base_keys_dir):
    for prefix in ('private', 'public', 'sig', 'verif', 'bls'):
        old_keys_dir = os.path.join(old_base_keys_dir, '{}_keys'.format(prefix))
        if os.path.exists(old_keys_dir) and os.path.isdir(old_keys_dir):
            shutil.move(old_keys_dir, new_base_keys_dir)


def _get_network_from_txn_file_name(file_name: str):
    name_split = file_name.split("_")
    ret_name = "sandbox"
    if name_split and name_split[-1] in ["live", "sandbox"]:
        ret_name = name_split[-1]
    return ret_name


def get_network_name():
    network_name = 'sandbox'
    old_general_config = os.path.join(old_base_dir, 'indy_config.py')
    spec = spec_from_file_location('old_general_config', old_general_config)
    old_cfg = module_from_spec(spec)
    spec.loader.exec_module(old_cfg)
    if hasattr(old_cfg, 'poolTransactionsFile'):
        network_name = _get_network_from_txn_file_name(old_cfg.poolTransactionsFile)
    elif hasattr(old_cfg, 'domainTransactionsFile'):
        network_name = _get_network_from_txn_file_name(old_cfg.domainTransactionsFile)
    elif hasattr(old_cfg, 'current_env') and old_cfg.current_env != 'test':
        network_name = old_cfg.current_env
    return network_name


def migrate_general_config(old_general_config, new_general_config, network_name):
    logger.info('Migrate general config file {} -> {} for network {}'.format(
        old_general_config, new_general_config, network_name))
    f = open(old_general_config, "r")
    lines = f.readlines()
    f.close()

    f = open(new_general_config, "w")
    for line in lines:
        if not line.startswith('current_env') and not line.startswith('poolTransactionsFile') and\
                not line.startswith('domainTransactionsFile'):
            f.write(line)
    line = "NETWORK_NAME = '{}'\n".format(network_name)
    f.write(line)
    f.close()


def migrate_cli(old_dir, new_dir, new_txn_dir):
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    # Move wallets directory
    logger.info('Move wallets directory {} -> {}'.format(
        old_dir, new_dir))
    shutil.move(old_dir, new_dir)
    logger.info('done')

    # Move txns for CLI
    migrate_genesis_txn(old_dir, new_txn_dir)


def migrate_all():
    base_dir = baseDir

    old_node_base_data_dir = os.path.join(old_base_dir, 'data')
    old_nodes_data_dir = os.path.join(old_node_base_data_dir, 'nodes')
    # old_wallets_dir = os.path.join(old_base_dir, 'wallets')
    old_general_config = os.path.join(old_base_dir, 'indy_config.py')
    old_daemon_config_base_dir = '/home/indy/.indy'
    old_daemon_config = os.path.join(old_daemon_config_base_dir, 'indy.env')

    new_general_config = os.path.join(GENERAL_CONFIG_DIR, GENERAL_CONFIG_FILE)

    logger.info('Start migration of directories/files.')

    # Check which network name should we use
    network_name = get_network_name()
    logger.info('Network name is {}'.format(network_name))

    # Migrate general config file
    migrate_general_config(old_general_config, new_general_config, network_name)

    # Build network-related paths
    new_log_dir = os.path.join(LOG_DIR, network_name)
    os.makedirs(new_log_dir, exist_ok=True)
    new_node_base_dir = os.path.join(base_dir, network_name)

    new_node_base_data_dir = os.path.join(NODE_BASE_DATA_DIR, network_name)
    new_node_base_data_dir = os.path.join(new_node_base_data_dir, "data")

    # Move genesis transactions
    migrate_genesis_txn(old_base_dir, NODE_BASE_DATA_DIR)

    try:
        visit_dirs = os.listdir(old_nodes_data_dir)
    except FileNotFoundError:
        visit_dirs = []

    for node_name in visit_dirs:
        # Move logs
        logger.info('Move logs for node \'{}\'...'.format(node_name))
        old_node_logs_exp = os.path.join(old_base_dir, '{}.log*'.format(node_name))
        for node_log in glob.glob(old_node_logs_exp):
            shutil.move(node_log, new_log_dir)
        logger.info('done')

        # Move keys
        logger.info('Move keys for node \'{}\'...'.format(node_name))
        old_keys_dir = os.path.join(old_base_dir, node_name)
        new_keys_dir = os.path.join(new_node_base_dir, "keys")
        new_keys_dir = os.path.join(new_keys_dir, node_name)
        os.makedirs(new_keys_dir, exist_ok=True)
        migrate_keys(old_keys_dir, new_keys_dir)
        logger.info('done')

    # Move nodes data directory
    logger.info('Move nodes data directory {} -> {}'.format(
        old_nodes_data_dir, new_node_base_data_dir))
    if os.path.exists(old_nodes_data_dir):
        shutil.move(old_nodes_data_dir, new_node_base_data_dir)
    logger.info('done')

    # Move daemon config
    logger.info('Move daemon config {} -> {}'.format(
        old_daemon_config, GENERAL_CONFIG_DIR))
    if os.path.exists(old_daemon_config):
        shutil.move(old_daemon_config, GENERAL_CONFIG_DIR)
    logger.info('done')

    # migrate_cli(old_wallets_dir, CLI_BASE_DIR, CLI_NETWORK_DIR)

    logger.info('Finish migration of directories/files.')


if not os.path.exists(old_base_dir):
    msg = 'Can not find old base directory \'{}\', abort migration.'.format(old_base_dir)
    logger.error(msg)
    raise Exception(msg)

migrate_all()
