import os

import shutil

_HOME_DIR = os.path.expanduser('~')
_LEGACY_DIR = os.path.expanduser('~/.sovrin')
_BASE_DIR = os.path.expanduser('~/.indy')
_BACKUP_DIR = os.path.expanduser('~/.indy-backup')

_DISTRIBUTED_FILE_NAMES = ['.indy',
                           '__pycache__',
                           'plugins',
                           'sample',
                           'indy_config.py',
                           'pool_transactions_local_genesis',
                           'pool_transactions_sandbox_genesis',
                           'pool_transactions_live_genesis']


def is_base_dir_untouched():
    if not os.path.exists(_BASE_DIR):
        return True

    if not os.path.isdir(_BASE_DIR):
        # In this abnormal case we believe that base directory has been modified
        return False

    for file_name in os.listdir(_BASE_DIR):
        if file_name not in _DISTRIBUTED_FILE_NAMES:
            return False

    return True


def legacy_base_dir_exists():
    return os.path.isdir(_LEGACY_DIR)


def _rename_if_exists(dir, old_name, new_name):
    if os.path.exists(os.path.join(dir, old_name)):
        os.rename(os.path.join(dir, old_name),
                  os.path.join(dir, new_name))


def _rename_request_files(requests_dir):
    for relative_name in os.listdir(requests_dir):
        absolute_name = os.path.join(requests_dir, relative_name)
        if os.path.isfile(absolute_name) \
                and absolute_name.endswith('.sovrin'):
            os.rename(absolute_name,
                      absolute_name[:-len('.sovrin')] + '.indy')


def _migrate_legacy_base_dir():
    shutil.copytree(_LEGACY_DIR, _BASE_DIR)

    _rename_if_exists(_BASE_DIR, '.sovrin', '.indy')
    _rename_if_exists(_BASE_DIR, 'sovrin_config.py', 'indy_config.py')

    if os.path.isdir(os.path.join(_BASE_DIR, 'sample')):
        _rename_request_files(os.path.join(_BASE_DIR, 'sample'))

    _rename_if_exists(_HOME_DIR, '.sovrin-cli-history', '.indy-cli-history')


def migrate():
    if os.path.isdir(_BACKUP_DIR):
        shutil.rmtree(_BACKUP_DIR)
    elif os.path.isfile(_BACKUP_DIR):
        os.remove(_BACKUP_DIR)

    if os.path.exists(_BASE_DIR):
        os.rename(_BASE_DIR, _BACKUP_DIR)

    try:
        _migrate_legacy_base_dir()
    except Exception as e:
        if os.path.exists(_BASE_DIR):
            shutil.rmtree(_BASE_DIR)
        if os.path.exists(_BACKUP_DIR):
            os.rename(_BACKUP_DIR, _BASE_DIR)
        _rename_if_exists(_HOME_DIR, '.indy-cli-history', '.sovrin-cli-history')
        raise e

    if os.path.exists(_BACKUP_DIR):
        shutil.rmtree(_BACKUP_DIR, ignore_errors=True)
