from plenum.common.constants import NODE_IP, CLIENT_IP, CLIENT_PORT, NODE_PORT, \
    ALIAS
from plenum.common.util import randomString
from plenum.test.cli.helper import exitFromCli
from stp_core.network.port_dispenser import genHa

from sovrin_client.test.cli.helper import doSendNodeCmd


def testAddNewNode(newNodeAdded):
    pass


def testConsecutiveAddSameNodeWithoutAnyChange(be, do, newStewardCli,
                                               newNodeVals, newNodeAdded):
    be(newStewardCli)
    doSendNodeCmd(do, newNodeVals,
              expMsgs=['node already has the same data as requested'])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNodeAndClientPortSame(be, do, newStewardCli,
                                                        newNodeVals,
                                                        newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    newNodeVals['newNodeData'][NODE_IP] = nodeIp
    newNodeVals['newNodeData'][NODE_PORT] = nodePort
    newNodeVals['newNodeData'][CLIENT_IP] = nodeIp
    newNodeVals['newNodeData'][CLIENT_PORT] = nodePort
    doSendNodeCmd(do, newNodeVals,
              expMsgs=["node and client ha cannot be same"])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNonAliasChange(be, do, newStewardCli,
                                                 newNodeVals, newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()
    newNodeVals['newNodeData'][NODE_IP] = nodeIp
    newNodeVals['newNodeData'][NODE_PORT] = nodePort
    newNodeVals['newNodeData'][CLIENT_IP] = nodeIp
    newNodeVals['newNodeData'][CLIENT_PORT] = clientPort
    doSendNodeCmd(do, newNodeVals)
    exitFromCli(do)


def testConsecutiveAddSameNodeWithOnlyAliasChange(be, do,
                                                  newStewardCli, newNodeVals,
                                                  newNodeAdded):
    be(newStewardCli)
    newNodeVals['newNodeData'][ALIAS] = randomString(6)
    doSendNodeCmd(do, newNodeVals,
              expMsgs=['existing data has conflicts with request data'])
    exitFromCli(do)
