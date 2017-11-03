import os

import shutil

from indy_client.utils.migration import ancient_migration
from indy_client.utils.migration import multinetworks_migration
from indy_client.utils.migration import rebranding_migration

_LEGACY_DIR = os.path.expanduser('~/.sovrin')
_TRANS_DIR = os.path.expanduser('~/.indy')
_CLI_BASE_DIR = os.path.expanduser('~/.indy-cli')
_BACKUP_DIR = os.path.expanduser('~/.indy-cli.backup')


def is_cli_base_dir_untouched():
    return not os.path.exists(os.path.join(_CLI_BASE_DIR, 'wallets'))


def legacy_base_dir_exists():
    return os.path.isdir(_LEGACY_DIR)


def migrate():
    if os.path.isdir(_BACKUP_DIR):
        shutil.rmtree(_BACKUP_DIR)
    elif os.path.isfile(_BACKUP_DIR):
        os.remove(_BACKUP_DIR)

    if os.path.exists(_CLI_BASE_DIR):
        os.rename(_CLI_BASE_DIR, _BACKUP_DIR)

    try:
        ancient_migration.migrate()
        rebranding_migration.migrate()
        multinetworks_migration.migrate()
    except Exception as e:
        if os.path.exists(_CLI_BASE_DIR):
            shutil.rmtree(_CLI_BASE_DIR)
        if os.path.exists(_BACKUP_DIR):
            os.rename(_BACKUP_DIR, _CLI_BASE_DIR)
        raise e
    finally:
        if os.path.exists(_TRANS_DIR):
            shutil.rmtree(_TRANS_DIR, ignore_errors=True)

    if os.path.exists(_BACKUP_DIR):
        shutil.rmtree(_BACKUP_DIR, ignore_errors=True)
