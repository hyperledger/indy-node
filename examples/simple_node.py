#! /usr/bin/env python3
"""
This is a simple script to start up a node. To see it in action, open up four
separate terminals, and in each one, run this script for a different node.

Usage:
simple_node.py <node_name>

Where <node_name> is one of Alpha, Beta, Gamma, Delta.

"""
import sys
from collections import OrderedDict
from tempfile import TemporaryDirectory

from stp_core.loop.looper import Looper
from plenum.common.constants import NYM
from indy_common.constants import TRUST_ANCHOR

from indy_node.server.node import Node


def run_node():

    nodeReg = OrderedDict([
        ('Alpha', ('127.0.0.1', 8001)),
        ('Beta', ('127.0.0.1', 8003)),
        ('Gamma', ('127.0.0.1', 8005)),
        ('Delta', ('127.0.0.1', 8007))])

    genesisTxns = [{'txnId': '6b86b273ff34fce19d6b804eff5a3f57'
                             '47ada4eaa22f1d49c01e52ddb7875b4b',
                    'type': NYM,
                    'dest': 'o7z4QmFkNB+mVkFI2BwX0Hdm1BGhnz8psWnKYIXWTaQ=',
                    'role': TRUST_ANCHOR}]

    # the first argument should be the node name
    try:
        nodeName = sys.argv[1]
    except IndexError:
        names = list(nodeReg.keys())
        print("Please supply a node name (one of {}) as the first argument.".
              format(", ".join(names)))
        print("For example:")
        print("    {} {}".format(sys.argv[0], names[0]))
        return

    with Looper(debug=False) as looper:
        # Nodes persist keys when bootstrapping to other nodes and reconnecting
        # using an ephemeral temporary directory when proving a concept is a
        # nice way to keep things tidy.
        with TemporaryDirectory() as tmpdir:
            node = Node(nodeName, nodeReg, basedirpath=tmpdir)
            node.addGenesisTxns(genesisTxns)
            looper.add(node)
            node.startKeySharing()
            looper.run()


if __name__ == '__main__':
    run_node()
