import os

import shutil
from importlib.util import module_from_spec, spec_from_file_location

_OLD_BASE_DIR = os.path.expanduser('~/.indy')
_CLI_BASE_DIR = os.path.expanduser('~/.indy-cli')
_CONFIG = 'indy_config.py'
_WALLETS = 'wallets'
_NETWORKS = 'networks'
_KEYS = 'keys'
_DATA = 'data'
_CLIENTS = 'clients'
_LEGACY_NETWORKS = ['live', 'local', 'sandbox']


# def _get_used_network_name():
#     old_config_path = os.path.join(_OLD_BASE_DIR, _CONFIG)
#     spec = spec_from_file_location('old_user_overrides', old_config_path)
#     old_user_overrides = module_from_spec(spec)
#     spec.loader.exec_module(old_user_overrides)
#
#     if hasattr(old_user_overrides, 'poolTransactionsFile'):
#         network_name = old_user_overrides.poolTransactionsFile.split('_')[-1]
#         if network_name in _LEGACY_NETWORKS:
#             return network_name
#
#     if hasattr(old_user_overrides, 'current_env') \
#             and old_user_overrides.current_env != 'test':
#         network_name = old_user_overrides.current_env
#         if network_name in _LEGACY_NETWORKS:
#             return network_name
#
#     return 'sandbox'


def _migrate_config():
    old_config_path = os.path.join(_OLD_BASE_DIR, _CONFIG)
    new_config_path = os.path.join(_CLI_BASE_DIR, _CONFIG)

    if os.path.isfile(old_config_path):
        with open(old_config_path, 'r') as old_config_file, \
                open(new_config_path, 'w') as new_config_file:
            for line in old_config_file:
                if not line.startswith('current_env') \
                        and not line.startswith('poolTransactionsFile') \
                        and not line.startswith('domainTransactionsFile'):
                    new_config_file.write(line)


def _migrate_genesis_txn_files():
    for network in _LEGACY_NETWORKS:
        old_genesis_pool_txn_path = os.path.join(
            _OLD_BASE_DIR, 'pool_transactions_{}_genesis'.format(network))
        new_genesis_pool_txn_path = os.path.join(
            _CLI_BASE_DIR, _NETWORKS, network, 'pool_transactions_genesis')

        if os.path.exists(old_genesis_pool_txn_path):
            os.makedirs(os.path.dirname(new_genesis_pool_txn_path),
                        exist_ok=True)
            shutil.copyfile(old_genesis_pool_txn_path,
                            new_genesis_pool_txn_path)


def _migrate_wallets():
    old_wallets_dir = os.path.join(_OLD_BASE_DIR, _WALLETS)
    new_wallets_dir = os.path.join(_CLI_BASE_DIR, _WALLETS)

    if os.path.isdir(old_wallets_dir):
        shutil.copytree(old_wallets_dir, new_wallets_dir)

        if os.path.exists(os.path.join(new_wallets_dir, 'test')):
            os.rename(os.path.join(new_wallets_dir, 'test'),
                      os.path.join(new_wallets_dir, 'sandbox'))


# def _migrate_keys(network):
#     old_data_dir = os.path.join(_OLD_BASE_DIR, _DATA, _CLIENTS)
#
#     for client in os.listdir(old_data_dir):
#         old_client_keys_dir = os.path.join(_OLD_BASE_DIR, client)
#         if os.path.isdir(old_client_keys_dir):
#             new_client_keys_dir = os.path.join(
#                 _CLI_BASE_DIR, _NETWORKS, network, _KEYS, client)
#             shutil.copytree(old_client_keys_dir, new_client_keys_dir)
#
#
# def _migrate_data(network):
#     old_data_dir = os.path.join(_OLD_BASE_DIR, _DATA, _CLIENTS)
#
#     for client in os.listdir(old_data_dir):
#         old_client_data_dir = os.path.join(old_data_dir, client)
#         if os.path.isdir(old_client_data_dir):
#             new_client_data_dir = os.path.join(
#                 _CLI_BASE_DIR, _NETWORKS, network, _DATA, _CLIENTS, client)
#             shutil.copytree(old_client_data_dir, new_client_data_dir)
#
#             sole_pool_txn_dir = os.path.join(new_client_data_dir,
#                                              'pool_transactions')
#             for specific_network in _LEGACY_NETWORKS:
#                 specific_pool_txn_dir = \
#                     os.path.join(new_client_data_dir,
#                                  'pool_transactions_{}'.format(specific_network))
#                 if os.path.isdir(specific_pool_txn_dir):
#                     if specific_network == network:
#                         os.rename(specific_pool_txn_dir, sole_pool_txn_dir)
#                     else:
#                         shutil.rmtree(specific_pool_txn_dir)


def migrate():
    os.makedirs(_CLI_BASE_DIR)

    # Used network cannot be determined for client in this way
    # network = _get_used_network_name()

    _migrate_config()
    _migrate_genesis_txn_files()
    _migrate_wallets()
    # Migration of keys and data is superfluous for client
    # _migrate_keys(network)
    # _migrate_data(network)
