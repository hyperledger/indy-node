import importlib
from importlib.util import module_from_spec, spec_from_file_location
import os

from stp_core.common.log import Logger, getlogger
from stp_core.types import HA
from stp_core.loop.looper import Looper

from indy_common.config_helper import NodeConfigHelper
from indy_node.server.node import Node


def integrate(node_config_helper, node, logger):
    plugin_root = node_config_helper.config.PLUGIN_ROOT
    try:
        plugin_root = importlib.import_module(plugin_root)
    except ImportError:
        raise ImportError('Incorrect plugin root {}. No such package found'.
                          format(plugin_root))
    enabled_plugins = node_config_helper.config.ENABLED_PLUGINS
    for plugin_name in enabled_plugins:
        importlib.import_module(plugin_name)
        main = importlib.import_module('{}.main'.format(plugin_name))
        logger.info('Going to integrate plugin: {}'.format(plugin_name))
        node = main.integrate_plugin_in_node(node)
        logger.info('Integrated plugin: {}'.format(plugin_name))
    return node


def run_node(config, name, node_ip, node_port, client_ip, client_port):
    node_ha = HA(node_ip, node_port)
    client_ha = HA(client_ip, client_port)

    node_config_helper = NodeConfigHelper(name, config)

    logFileName = os.path.join(node_config_helper.log_dir, name + ".log")

    logger = getlogger()
    Logger().apply_config(config)
    Logger().enableFileLogging(logFileName)

    logger.setLevel(config.logLevel)
    logger.debug("You can find logs in {}".format(logFileName))

    vars = [var for var in os.environ.keys() if var.startswith("INDY")]
    logger.debug("Indy related env vars: {}".format(vars))

    with Looper(debug=config.LOOPER_DEBUG) as looper:
        node = Node(name,
                    config_helper=node_config_helper,
                    ha=node_ha, cliha=client_ha)
        node = integrate(node_config_helper, node, logger)
        looper.add(node)
        looper.run()
