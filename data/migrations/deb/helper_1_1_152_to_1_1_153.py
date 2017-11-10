import os
import shutil

from indy_common.config_util import getConfig
from stp_core.common.log import getlogger

config = getConfig()
logger = getlogger()


def _get_nodes_data_dir():
    base_dir = os.path.expanduser(config.baseDir)
    nodes_data_dir = os.path.join(base_dir, config.NETWORK_NAME, config.nodeDataDir)
    if not os.path.exists(nodes_data_dir):
        msg = 'Can not find the directory with the ledger: {}'.format(nodes_data_dir)
        logger.error(msg)
        raise Exception(msg)
    return nodes_data_dir


def rm_if_exist(base_dir, sub_dirs):
    for sd in sub_dirs:
        to_del = os.path.join(base_dir, sd)
        if os.path.isdir(to_del):
            shutil.rmtree(to_del)


def migrate_all_states(node_data_directory):
    # the states will be recovered from the ledger during the start-up.
    # just delete the current ones
    rm_if_exist(node_data_directory, ['pool_state', 'domain_state', 'config_state', 'idr_cache_db'])


def migrate_all():
    nodes_data_dir = _get_nodes_data_dir()
    for node_dir in os.listdir(nodes_data_dir):
        node_data_dir = os.path.join(nodes_data_dir, node_dir)
        logger.info("Applying migration to {}".format(node_data_dir))
        migrate_all_states(node_data_dir)


migrate_all()
