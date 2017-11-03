import os

import shutil

from ledger.genesis_txn.genesis_txn_file_util import genesis_txn_file

_BASE_DIR = os.path.expanduser('~/.sovrin')
_BACKUP_DIR = os.path.expanduser('~/.sovrin.backup')
_NETWORKS = ['live', 'local', 'sandbox']


def _update_wallets_dir_name_if_outdated():
    old_named_path = os.path.expanduser(os.path.join(_BASE_DIR, 'keyrings'))
    new_named_path = os.path.expanduser(os.path.join(_BASE_DIR, 'wallets'))
    if not os.path.exists(new_named_path) and os.path.isdir(old_named_path):
        os.rename(old_named_path, new_named_path)


def _update_genesis_txn_file_name_if_outdated(transaction_file):
    old_named_path = os.path.join(_BASE_DIR, transaction_file)
    new_named_path = os.path.join(_BASE_DIR, genesis_txn_file(transaction_file))
    if not os.path.exists(new_named_path) and os.path.isfile(old_named_path):
        os.rename(old_named_path, new_named_path)


def _migrate_wallets_dir_and_genesis_txn_files():
    _update_wallets_dir_name_if_outdated()
    for network in _NETWORKS:
        _update_genesis_txn_file_name_if_outdated(
            'pool_transactions_{}'.format(network))


def migrate():
    if os.path.isdir(_BACKUP_DIR):
        shutil.rmtree(_BACKUP_DIR)
    elif os.path.isfile(_BACKUP_DIR):
        os.remove(_BACKUP_DIR)

    os.rename(_BASE_DIR, _BACKUP_DIR)

    try:
        shutil.copytree(_BACKUP_DIR, _BASE_DIR)
        _migrate_wallets_dir_and_genesis_txn_files()
    except Exception as e:
        if os.path.exists(_BASE_DIR):
            shutil.rmtree(_BASE_DIR)
        os.rename(_BACKUP_DIR, _BASE_DIR)
        raise e

    shutil.rmtree(_BACKUP_DIR, ignore_errors=True)
