#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os

from stp_core.common.log import Logger, getlogger
from stp_core.types import HA


def run_node(config, name, node_port, client_port):
    node_ha = HA("0.0.0.0", node_port)
    client_ha = HA("0.0.0.0", client_port)

    logFileName = os.path.join(config.LOG_DIR, config.NETWORK_NAME, name + ".log")

    Logger(config)
    Logger().enableFileLogging(logFileName)

    logger = getlogger()
    logger.setLevel(config.logLevel)
    logger.debug("You can find logs in {}".format(logFileName))

    vars = [var for var in os.environ.keys() if var.startswith("INDY")]
    logger.debug("Indy related env vars: {}".format(vars))

    node_base_dir = os.path.join(config.baseDir, config.NETWORK_NAME)
    node_base_data_dir = os.path.join(config.NODE_BASE_DATA_DIR, config.NETWORK_NAME)

    from stp_core.loop.looper import Looper
    from indy_node.server.node import Node
    with Looper(debug=config.LOOPER_DEBUG) as looper:
        node = Node(name, nodeRegistry=None, basedirpath=node_base_dir,
                    base_data_dir=node_base_data_dir,
                    ha=node_ha, cliha=client_ha)
        looper.add(node)
        looper.run()
