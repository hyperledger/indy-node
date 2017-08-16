import shutil

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.util import randomString
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data, \
    waitNodeDataEquality
from plenum.test.test_node import checkNodesConnected, ensure_node_disconnected
from sovrin_client.test.helper import getClientAddedWithRole
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_node.test.helper import addRawAttribute, TestNode


TestRunningTimeLimitSec = 200


def test_state_regenerated_from_ledger(looper, tdirWithPoolTxns,
                                            tdirWithDomainTxnsUpdated,
                                            nodeSet, tconf,
                                            trustee, trusteeWallet,
                                            allPluginsPath):
    """
    Node loses its state database but recreates it from ledger after start.
    Checking ATTRIB txns too since they store some data off ledger too
    """
    trust_anchors = []
    for i in range(5):
        trust_anchors.append(getClientAddedWithRole(nodeSet,
                                                    tdirWithPoolTxns, looper,
                                                    trustee, trusteeWallet,
                                                    'TA' + str(i),
                                                    role=TRUST_ANCHOR))
        addRawAttribute(looper, *trust_anchors[-1], randomString(6),
                        randomString(10), dest=trust_anchors[-1][1].defaultId)

    for tc, tw in trust_anchors:
        for i in range(3):
            getClientAddedWithRole(nodeSet,
                                 tdirWithPoolTxns,
                                 looper,
                                 tc, tw,
                                 'NP1' + str(i))

    ensure_all_nodes_have_same_data(looper, nodeSet)

    node_to_stop = nodeSet[-1]
    node_state = node_to_stop.states[DOMAIN_LEDGER_ID]
    assert not node_state.isEmpty
    state_db_path = node_state._kv.db_path
    node_to_stop.cleanupOnStopping = False
    node_to_stop.stop()
    looper.removeProdable(node_to_stop)
    ensure_node_disconnected(looper, node_to_stop.name, nodeSet[:-1])

    shutil.rmtree(state_db_path)

    restarted_node = TestNode(node_to_stop.name, basedirpath=tdirWithPoolTxns,
                        config=tconf, pluginPaths=allPluginsPath,
                        ha=node_to_stop.nodestack.ha, cliha=node_to_stop.clientstack.ha)
    looper.add(restarted_node)
    nodeSet[-1] = restarted_node

    looper.run(checkNodesConnected(nodeSet))
    # Need some time as `last_ordered_3PC` is compared too and that is
    # communicated through catchup
    waitNodeDataEquality(looper, restarted_node, *nodeSet[:-1])

    # Pool is still functional
    for tc, tw in trust_anchors:
        getClientAddedWithRole(nodeSet,
                             tdirWithPoolTxns,
                             looper,
                             tc, tw,
                             'NP--{}'.format(tc.name))

    ensure_all_nodes_have_same_data(looper, nodeSet)
