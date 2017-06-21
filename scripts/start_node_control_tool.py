#!/usr/bin/python3

import argparse
from sovrin_node.utils.node_control_tool import NodeControlTool


# Parse command line arguments
test_mode = False
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="runs in special Test mode",
                    action="store_true")
args = parser.parse_args()
if args.test:
    test_mode = True

nodeControlTool = NodeControlTool(test_mode = test_mode)
nodeControlTool.start()
    


