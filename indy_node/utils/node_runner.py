import os

from stp_core.common.log import Logger, getlogger
from stp_core.types import HA
from stp_core.loop.looper import Looper

from indy_common.config_helper import NodeConfigHelper
from indy_node.server.node import Node


def run_node(config, name, node_port, client_port):
    node_ha = HA("0.0.0.0", node_port)
    client_ha = HA("0.0.0.0", client_port)

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
        node = Node(name, nodeRegistry=None,
                    config_helper=node_config_helper,
                    ha=node_ha, cliha=client_ha)
        looper.add(node)
        looper.run()
