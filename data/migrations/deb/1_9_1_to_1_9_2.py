import os
import shutil

from indy_common.config_helper import NodeConfigHelper
from indy_common.config_util import getConfig
from stp_core.common.log import getlogger


logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"
BUILDER_NET_NETWORK_NAME = "net3"


def get_node_name():
    node_name = None
    node_name_key = 'NODE_NAME'

    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as fenv:
            for line in fenv.readlines():
                if line.find(node_name_key) != -1:
                    node_name = line.split('=')[1].strip()
                    break
    if node_name is None:
        logger.error("{} file doesn't contains a node name. Please add string like NODE_NAME=<node name> into this file".format(ENV_FILE_PATH))

    return node_name


def remove_dir(path_to_dir):
    try:
        shutil.rmtree(path_to_dir)
    except shutil.Error as ex:
        logger.error("""While removing directory: {} the next error was raised:
{}""".format(path_to_dir, ex))

        return False
    return True


def migrate_all():

    node_name = get_node_name()
    if node_name is None:
        return False

    config = getConfig()
    config_helper = NodeConfigHelper(node_name, config)

    if BUILDER_NET_NETWORK_NAME != config.NETWORK_NAME:
        logger.info("This script can be used only for {} network".format(BUILDER_NET_NETWORK_NAME))
        return False

    path_to_config_state = os.path.join(config_helper.ledger_dir, config.configStateDbName)
    path_to_config_ts_db = os.path.join(config_helper.ledger_dir, config.configStateTsDbName)

    if not os.path.exists(path_to_config_ts_db):
        logger.error("Path {} to config's timestamp storage does not exist".format(path_to_config_ts_db))
        return False

    if not os.path.exists(path_to_config_state):
        logger.error("Path {} to config_state storage does not exist".format(path_to_config_state))
        return False

    if not remove_dir(path_to_config_ts_db):
        logger.error("Failed to remove {}".format(path_to_config_ts_db))
        return False

    if not remove_dir(path_to_config_state):
        logger.error("Failed to remove {}".format(path_to_config_state))
        return False

    logger.info("Config state storage was successfully removed. Path was {}".format(path_to_config_state))

    return True


if not migrate_all():
    logger.error("Config state storage removing failed")
