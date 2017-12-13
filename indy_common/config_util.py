from importlib import import_module

from plenum.common.config_util import getConfig as PlenumConfig, \
    getConfigOnce as PlenumConfigOnce, extend_with_default_external_config


CONFIG = None


def _getConfig(plenum_config_func,
               general_config_dir=None,
               user_config_dir=None):
    config = plenum_config_func(general_config_dir)
    indyConfig = import_module("indy_common.config")
    config.__dict__.update(indyConfig.__dict__)

    extend_with_default_external_config(config,
                                        general_config_dir=general_config_dir,
                                        user_config_dir=user_config_dir)
    return config


def getConfig(general_config_dir=None, user_config_dir=None):
    global CONFIG
    if not CONFIG:
        CONFIG = _getConfig(PlenumConfig, general_config_dir, user_config_dir)
    return CONFIG


def getConfigOnce(general_config_dir=None, user_config_dir=None):
    return _getConfig(PlenumConfigOnce, general_config_dir, user_config_dir)
