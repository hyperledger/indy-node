import os

import shutil

_HOME_DIR = os.path.expanduser('~')
_LEGACY_BASE_DIR = os.path.expanduser('~/.sovrin')
_BASE_DIR = os.path.expanduser('~/.indy')


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


def migrate():
    shutil.copytree(_LEGACY_BASE_DIR, _BASE_DIR)

    _rename_if_exists(_BASE_DIR, '.sovrin', '.indy')
    _rename_if_exists(_BASE_DIR, 'sovrin_config.py', 'indy_config.py')

    if os.path.isdir(os.path.join(_BASE_DIR, 'sample')):
        _rename_request_files(os.path.join(_BASE_DIR, 'sample'))

    _rename_if_exists(_HOME_DIR, '.sovrin-cli-history', '.indy-cli-history')
