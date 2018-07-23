import os

from indy_common.config import GENERAL_CONFIG_DIR


def create_config_dirs(base_dir):
    gen_conf_dir_default = GENERAL_CONFIG_DIR.lstrip('/') \
        if GENERAL_CONFIG_DIR.startswith('/') else GENERAL_CONFIG_DIR

    general_config_dir = os.path.join(base_dir, gen_conf_dir_default)
    os.makedirs(general_config_dir)

    return general_config_dir
