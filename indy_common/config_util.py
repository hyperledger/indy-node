import os
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location

from plenum.common.config_util import getConfig as PlenumConfig, \
    extend_with_default_external_config


CONFIG = None


def getConfig(user_config_dir=None):
    global CONFIG
    if not CONFIG:
        config = PlenumConfig(user_config_dir)
        indyConfig = import_module("indy_common.config")
        config.__dict__.update(indyConfig.__dict__)

        extend_with_default_external_config(config, user_config_dir)

        CONFIG = config
    return CONFIG
