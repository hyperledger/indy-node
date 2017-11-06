import os

import shutil

from indy_client.utils.migration import ancient_migration
from indy_client.utils.migration import multi_network_migration
from indy_client.utils.migration import rebranding_migration

_HOME_DIR = os.path.expanduser('~')
_LEGACY_BASE_DIR = os.path.expanduser('~/.sovrin')
_LEGACY_BASE_BACKUP_DIR = os.path.expanduser('~/.sovrin.backup')
_TRANS_BASE_DIR = os.path.expanduser('~/.indy')
_CLI_BASE_DIR = os.path.expanduser('~/.indy-cli')
_CLI_BASE_BACKUP_DIR = os.path.expanduser('~/.indy-cli.backup')


def is_cli_base_dir_untouched():
    return not os.path.exists(os.path.join(_CLI_BASE_DIR, 'wallets'))


def legacy_base_dir_exists():
    return os.path.isdir(_LEGACY_BASE_DIR)


def _remove_path_if_exists(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def _try_remove_path(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        print(e)


def migrate():
    _remove_path_if_exists(_LEGACY_BASE_BACKUP_DIR)
    _remove_path_if_exists(_CLI_BASE_BACKUP_DIR)
    _remove_path_if_exists(_TRANS_BASE_DIR)
    _remove_path_if_exists(os.path.join(_HOME_DIR, '.indy-cli-history'))

    try:
        os.rename(_LEGACY_BASE_DIR, _LEGACY_BASE_BACKUP_DIR)
        shutil.copytree(_LEGACY_BASE_BACKUP_DIR, _LEGACY_BASE_DIR)

        if os.path.exists(_CLI_BASE_DIR):
            os.rename(_CLI_BASE_DIR, _CLI_BASE_BACKUP_DIR)

        ancient_migration.migrate()
        rebranding_migration.migrate()
        multi_network_migration.migrate()

    except Exception as e:
        if os.path.exists(_CLI_BASE_BACKUP_DIR):
            _remove_path_if_exists(_CLI_BASE_DIR)
            os.rename(_CLI_BASE_BACKUP_DIR, _CLI_BASE_DIR)

        if os.path.exists(os.path.join(_HOME_DIR, '.indy-cli-history')):
            os.rename(os.path.join(_HOME_DIR, '.indy-cli-history'),
                      os.path.join(_HOME_DIR, '.sovrin-cli-history'))

        raise e

    finally:
        # We restore .sovrin from backup anyway to preserve
        # untouched pre-migration data because the ancient migration
        # makes changes right in .sovrin
        if os.path.exists(_LEGACY_BASE_BACKUP_DIR):
            _remove_path_if_exists(_LEGACY_BASE_DIR)
            os.rename(_LEGACY_BASE_BACKUP_DIR, _LEGACY_BASE_DIR)

        # We should remove the transitional base directory (.indy) anyway
        _try_remove_path(_TRANS_BASE_DIR)

    # Since the migration has succeeded, we remove .indy-cli.backup
    _try_remove_path(_CLI_BASE_BACKUP_DIR)
