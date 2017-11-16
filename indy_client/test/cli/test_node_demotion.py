import pytest
from plenum.common.signer_did import DidSigner
from stp_core.crypto.util import randomSeed
from indy_client.test.cli.helper import addAgent
from plenum.common.constants import SERVICES, VALIDATOR, TARGET_NYM, DATA
from indy_client.test.cli.constants import NODE_REQUEST_COMPLETED, NODE_REQUEST_FAILED


def ensurePoolIsOperable(be, do, cli):
    randomNymMapper = {
        'remote': DidSigner(seed=randomSeed()).identifier
    }
    addAgent(be, do, cli, randomNymMapper)


# this test messes with other tests so it goes in its own module
def test_steward_can_promote_and_demote_own_node(
        be, do, poolNodesStarted, newStewardCli, trusteeCli, newNodeVals):

    ensurePoolIsOperable(be, do, newStewardCli)

    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_COMPLETED, within=8)

    newNodeVals['newNodeData'][SERVICES] = []

    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_COMPLETED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)

    for node in poolNodesStarted.nodes.values():
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        assert txn[TARGET_NYM] == newNodeVals['newNodeIdr']
        assert SERVICES in txn[DATA] and txn[DATA][SERVICES] == []

    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR]

    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_COMPLETED, within=8)

    for node in poolNodesStarted.nodes.values():
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        assert txn[TARGET_NYM] == newNodeVals['newNodeIdr']
        assert SERVICES in txn[DATA] and txn[DATA][SERVICES] == [VALIDATOR]
