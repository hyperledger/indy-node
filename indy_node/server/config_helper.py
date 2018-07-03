import os

from indy_node.general_config import general_config

from indy_common.config import GENERAL_CONFIG_DIR, GENERAL_CONFIG_FILE
from indy_node.general_config import ubuntu_platform_config, \
    windows_platform_config


def create_config_dirs(base_dir, platform='ubuntu'):
    if platform == 'ubuntu':
        platform_config = ubuntu_platform_config
    elif platform == 'windows':
        platform_config = windows_platform_config
    else:
        raise RuntimeError('Unknown platform {}. Cannot load config'.format(platform))

    gen_conf_dir_default = GENERAL_CONFIG_DIR.lstrip('/') \
        if GENERAL_CONFIG_DIR.startswith('/') else GENERAL_CONFIG_DIR

    general_config_dir = os.path.join(base_dir, gen_conf_dir_default)
    os.makedirs(general_config_dir)
    general_config_path = os.path.join(general_config_dir,
                                       GENERAL_CONFIG_FILE)

    with open(general_config.__file__, 'r') as general_config_file:
        lines = general_config_file.readlines()
        with open(platform_config.__file__, 'r') as platform_config_file:
            with open(general_config_path,
                      'w') as general_config_result_file:
                for line in lines:
                    if line.startswith('NETWORK_NAME'):
                        line = 'NETWORK_NAME = \'sandbox\'\n'
                    general_config_result_file.write(line)
                general_config_result_file.write(
                    platform_config_file.read())

    return general_config_dir
