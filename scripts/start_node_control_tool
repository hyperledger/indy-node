#! /usr/bin/env python3

import argparse

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

    nodeControlTool = NodeControlTool(test_mode=args.test,
                                      hold_ext=args.hold_ext)
    nodeControlTool.start()
