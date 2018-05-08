import base58

from plenum.common.constants import NODE_IP, CLIENT_IP, CLIENT_PORT, NODE_PORT, \
    ALIAS, BLS_KEY
from plenum.common.util import randomString
from plenum.test.cli.helper import exitFromCli
from stp_core.network.port_dispenser import genHa

from indy_client.test.cli.helper import doSendNodeCmd


def test_add_new_node(newNodeAdded):
    '''
    Checks adding of a new Nodes with all parameters (including BLS keys)
    '''
    pass


def test_add_same_node_without_any_change(be, do, newStewardCli,
                                          newNodeVals, newNodeAdded):
    '''
    Checks that it's not possible to add the same node twice by owner
    '''
    be(newStewardCli)
    doSendNodeCmd(do, newNodeVals,
                  expMsgs=['node already has the same data as requested'])
    exitFromCli(do)


def test_add_same_node_without_any_change_by_trustee(be, do, trusteeCli,
                                                     newNodeVals, newNodeAdded,
                                                     nodeValsEmptyData):
    '''
    Checks that it's not possible to add the same node twice by Trustee
    '''
    be(trusteeCli)
    doSendNodeCmd(do, newNodeVals,
                  expMsgs=["node already has the same data as requested"])
    exitFromCli(do)


def test_add_same_node_with_changed_bls_by_trustee(be, do, trusteeCli,
                                                   newNodeVals, newNodeAdded,
                                                   nodeValsEmptyData):
    '''
    Checks that it's not possible to add the same node with different BLS key by Trustee
    '''
    be(trusteeCli)
    node_vals = newNodeVals
    node_vals['newNodeData'][BLS_KEY] = base58.b58encode(randomString(128).encode()).decode("utf-8")
    doSendNodeCmd(do, node_vals,
                  expMsgs=["TRUSTEE not in allowed roles ['STEWARD']"])
    exitFromCli(do)


def test_update_node_and_client_port_same(be, do, newStewardCli,
                                          newNodeVals,
                                          newNodeAdded,
                                          nodeValsEmptyData):
    '''
    Checks that it's not possible to have node and client ports same (by owner)
    '''
    be(newStewardCli)
    nodeIp, nodePort = genHa()

    node_vals = nodeValsEmptyData
    node_vals['newNodeData'][ALIAS] = newNodeVals['newNodeData'][ALIAS]
    node_vals['newNodeData'][NODE_IP] = nodeIp
    node_vals['newNodeData'][NODE_PORT] = nodePort
    node_vals['newNodeData'][CLIENT_IP] = nodeIp
    node_vals['newNodeData'][CLIENT_PORT] = nodePort

    doSendNodeCmd(do, node_vals,
                  expMsgs=["node and client ha cannot be same"])
    exitFromCli(do)


def test_update_ports_and_ips(be, do, newStewardCli,
                              newNodeVals, newNodeAdded,
                              nodeValsEmptyData):
    '''
    Checks that it's possible to update node and client ports and IPs (by owner)
    (just alias and ports/IPs are required)
    '''
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()

    node_vals = nodeValsEmptyData
    node_vals['newNodeData'][ALIAS] = newNodeVals['newNodeData'][ALIAS]
    node_vals['newNodeData'][NODE_IP] = nodeIp
    node_vals['newNodeData'][NODE_PORT] = nodePort
    node_vals['newNodeData'][CLIENT_IP] = clientIp
    node_vals['newNodeData'][CLIENT_PORT] = clientPort

    doSendNodeCmd(do, node_vals,
                  expMsgs=['Node request completed'])
    exitFromCli(do)


def test_update_bls(be, do, newStewardCli,
                    newNodeVals, newNodeAdded,
                    nodeValsEmptyData):
    '''
    Checks that it's possible to update BLS keys by owner (just alias and new key are required)
    '''
    be(newStewardCli)

    node_vals = nodeValsEmptyData
    node_vals['newNodeData'][ALIAS] = newNodeVals['newNodeData'][ALIAS]
    node_vals['newNodeData'][BLS_KEY] = base58.b58encode(randomString(128).encode()).decode("utf-8")

    doSendNodeCmd(do, node_vals,
                  expMsgs=['Node request completed'])
    exitFromCli(do)


def test_update_bls_by_trustee(be, do, trusteeCli,
                               newNodeVals, newNodeAdded,
                               nodeValsEmptyData):
    '''
    Checks that it's not possible to update BLS keys by Trustee (just alias and new key are required)
    '''
    be(trusteeCli)

    node_vals = nodeValsEmptyData
    node_vals['newNodeData'][ALIAS] = newNodeVals['newNodeData'][ALIAS]
    node_vals['newNodeData'][BLS_KEY] = base58.b58encode(randomString(128).encode()).decode("utf-8")

    doSendNodeCmd(do, node_vals,
                  expMsgs=["TRUSTEE not in allowed roles ['STEWARD']"])
    exitFromCli(do)


def test_add_same_data_alias_changed(be, do,
                                     newStewardCli, newNodeVals,
                                     newNodeAdded):
    '''
    Checks that it's not possible to add a new Node with the same alias (by owner)
    '''
    be(newStewardCli)
    newNodeVals['newNodeData'][ALIAS] = randomString(6)
    doSendNodeCmd(do, newNodeVals,
                  expMsgs=['existing data has conflicts with request data'])
    exitFromCli(do)


def test_update_alias(be, do,
                      newStewardCli,
                      newNodeAdded,
                      nodeValsEmptyData):
    '''
    Checks that it's not possible to change alias of existing node (by owner)
    '''
    be(newStewardCli)

    node_vals = nodeValsEmptyData
    node_vals['newNodeData'][ALIAS] = randomString(6)

    doSendNodeCmd(do, node_vals,
                  expMsgs=['existing data has conflicts with request data'])
    exitFromCli(do)
