import os

from stp_core.common.log import Logger, getlogger
from stp_core.types import HA


def run_node(config, name, node_port, client_port):
    node_ha = HA("0.0.0.0", node_port)
    client_ha = HA("0.0.0.0", client_port)

    logFileName = os.path.join(config.baseDir, name + ".log")

    Logger(config)
    Logger().enableFileLogging(logFileName)

    logger = getlogger()
    logger.setLevel(config.logLevel)
    logger.debug("You can find logs in {}".format(logFileName))

    vars = [var for var in os.environ.keys() if var.startswith("SOVRIN")]
    logger.debug("Sovrin related env vars: {}".format(vars))

    from stp_core.loop.looper import Looper
    from sovrin_node.server.node import Node
    with Looper(debug=config.LOOPER_DEBUG) as looper:
        node = Node(name, nodeRegistry=None, basedirpath=config.baseDir,
                    ha=node_ha, cliha=client_ha)
        looper.add(node)
        looper.run()
