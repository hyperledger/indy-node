#!/usr/bin/python3

import argparse
from sovrin_node.utils.node_control_tool import NodeControlTool


# Parse command line arguments
test_mode = False
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="runs in special Test mode",
                    action="store_true")
parser.add_argument(
    "--hold-ext",
    type=str,
    help="list of additional packages to disable auto upgrade for (Linux only)",
    default='')
args = parser.parse_args()
if args.test:
    test_mode = True

nodeControlTool = NodeControlTool(test_mode=test_mode, hold_ext=args.hold_ext)
nodeControlTool.start()
