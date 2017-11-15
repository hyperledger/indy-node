from plenum.common.constants import SERVICES, VALIDATOR, TARGET_NYM, DATA
from indy_common.roles import Roles
from stp_core.network.port_dispenser import genHa

import pytest

from indy_client.test.cli.helper import doSendNodeCmd


def testSuspendNode(be, do, trusteeCli, newNodeAdded):
    """
    Suspend a node and then cancel suspension. Suspend while suspended
    to test that there is no error
    """
    newNodeVals = newNodeAdded

    be(trusteeCli)

    newNodeVals['newNodeData'][SERVICES] = []
    doSendNodeCmd(do, newNodeVals)
    # Re-suspend node
    newNodeVals['newNodeData'][SERVICES] = []
    doSendNodeCmd(do, newNodeVals,
                  expMsgs=['node already has the same data as requested'])

    # Cancel suspension
    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR]
    doSendNodeCmd(do, newNodeVals)

    # Re-cancel suspension
    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR]
    doSendNodeCmd(do, nodeVals=newNodeVals,
                  expMsgs=['node already has the same data as requested'])


@pytest.mark.skip(reason='INDY-133. Broken compatibility')
def testSuspendNodeWhichWasNeverActive(be, do, trusteeCli, nymAddedOut,
                                       poolNodesStarted, trusteeMap):
    """
    Add a node without services field and check that the ledger does not
    contain the `services` field and check that it can be blacklisted and
    the ledger has `services` as empty list
    """
    newStewardSeed = '0000000000000000000KellySteward2'
    newStewardIdr = 'DqCx7RFEpSUMZbV2mH89XPH6JT3jMvDNU55NTnBHsQCs'
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role}'.format(
        role=Roles.STEWARD.name),
       within=5,
       expect=nymAddedOut, mapper={'remote': newStewardIdr})
    do('new key with seed {}'.format(newStewardSeed))
    nport, cport = (_[1] for _ in genHa(2))
    nodeId = '6G9QhQa3HWjRKeRmEvEkLbWWf2t7cw6KLtafzi494G4G'
    newNodeVals = {
        'newNodeIdr': nodeId,
        'newNodeData': {'client_port': cport,
                        'client_ip': '127.0.0.1',
                        'alias': 'Node6',
                        'node_ip': '127.0.0.1',
                        'node_port': nport
                        }
    }
    doSendNodeCmd(do, newNodeVals)

    for node in poolNodesStarted.nodes.values():
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        assert txn[TARGET_NYM] == nodeId
        assert SERVICES not in txn[DATA]

    do('new key with seed {}'.format(trusteeMap['trusteeSeed']))
    newNodeVals['newNodeData'][SERVICES] = []
    doSendNodeCmd(do, newNodeVals)

    for node in poolNodesStarted.nodes.values():
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        assert txn[TARGET_NYM] == nodeId
        assert SERVICES in txn[DATA] and txn[DATA][SERVICES] == []
