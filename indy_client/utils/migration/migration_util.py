import os

_LEGACY_DIR = os.path.expanduser('~/.sovrin')
_CLI_BASE_DIR = os.path.expanduser('~/.indy-cli')
_WALLETS = '/wallets'


def is_base_dir_untouched():
    return not os.path.exists(os.path.join(_CLI_BASE_DIR, _WALLETS))


def legacy_base_dir_exists():
    return os.path.isdir(_LEGACY_DIR)
