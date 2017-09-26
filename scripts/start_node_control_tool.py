#!/usr/bin/python3

import argparse
import os

from stp_core.common.log import Logger

from indy_common.config_util import getConfig
from indy_node.utils.node_control_tool import NodeControlTool

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="runs in special Test mode",
                        action="store_true")
    parser.add_argument(
        "--hold-ext",
        type=str,
        help="list of additional packages to disable auto upgrade for"
             " (Linux only)",
        default="")
    args = parser.parse_args()

    config = getConfig()
    Logger(config).enableFileLogging(
        os.path.join(config.baseDir, config.controlServiceLogFile))

    nodeControlTool = NodeControlTool(base_dir=config.baseDir,
                                      test_mode=args.test,
                                      hold_ext=args.hold_ext)
    nodeControlTool.start()
