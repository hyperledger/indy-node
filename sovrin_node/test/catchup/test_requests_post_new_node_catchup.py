from plenum.test.node_catchup.helper import checkNodeLedgersForEquality, \
    waitNodeLedgersEquality
from sovrin_client.test.client.TestClient import TestClient
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_client.test.helper import getClientAddedWithRole

from sovrin_node.test.conftest import nodeThetaAdded
from sovrin_node.test.helper import TestNode


def test_new_node_catchup_update_graph(looper, tdirWithPoolTxns,
                                        tdirWithDomainTxnsUpdated,
                                        nodeSet, tconf,
                                        trustee, trusteeWallet,
                                        allPluginsPath):
    """
    4 nodes start up and some txns happen, after txns are done, new node joins
    and starts catching up, the node should not process requests while catchup
    is in progress. Make sure the new requests are coming from the new NYMs
    added while the node was offline or catching up.
    """
    # Create a new node and stop it.

    new_steward, new_steward_wallet, new_node = nodeThetaAdded(looper,
                                                               nodeSet,
                                                               tdirWithPoolTxns,
                                                               tconf, trustee,
                                                               trusteeWallet,
                                                               allPluginsPath,
                                                               TestNode,
                                                               TestClient,
                                                               tdirWithPoolTxns)

    waitNodeLedgersEquality(looper, new_node, *nodeSet[:-1])
    ta_count = 5
    np_count = 5
    new_txn_count = ta_count + np_count
    old_ledger_sizes = {}
    new_ledger_sizes = {}
    old_projection_sizes = {}
    new_projection_sizes = {}

    def get_ledger_size(node):
        return len(node.domainLedger)

    def get_projection_size(node):
        return len(node.graphStore.client.command('select * from Nym'))

    def fill_counters(ls, ps, nodes):
        for n in nodes:
            ls[n.name] = get_ledger_size(n)
            ps[n.name] = get_projection_size(n)

    def check_sizes(nodes):
        for node in nodes:
            assert new_ledger_sizes[node.name] - old_ledger_sizes[node.name] == new_txn_count
            assert new_projection_sizes[node.name] - old_projection_sizes[node.name] == new_txn_count

    # Stop a node and note down the sizes of ledger and projection (orientdb)
    other_nodes = nodeSet[:-1]
    fill_counters(old_ledger_sizes, old_projection_sizes, other_nodes)
    new_node.cleanupOnStopping = False
    new_node.stop()
    looper.removeProdable(new_node)

    trust_anchors = []

    for i in range(ta_count):
        trust_anchors.append(getClientAddedWithRole(other_nodes,
                                                    tdirWithPoolTxns, looper,
                                                    trustee, trusteeWallet,
                                                    'TA'+str(i), TRUST_ANCHOR,
                                                    client_connects_to=len(other_nodes)))

    non_privileged = []
    for i in range(np_count):
        non_privileged.append(getClientAddedWithRole(other_nodes,
                                                    tdirWithPoolTxns, looper,
                                                    trustee, trusteeWallet,
                                                    'NP'+str(i),
                                                     client_connects_to=len(other_nodes)))

    checkNodeLedgersForEquality(nodeSet[0], *other_nodes)
    fill_counters(new_ledger_sizes, new_projection_sizes, other_nodes)
    # The size difference should be same as number of new NYM txns
    check_sizes(other_nodes)

    new_node = TestNode(new_node.name, basedirpath=tdirWithPoolTxns,
                        config=tconf, pluginPaths=allPluginsPath,
                        ha=new_node.nodestack.ha, cliha=new_node.clientstack.ha)
    looper.add(new_node)
    nodeSet[-1] = new_node
    fill_counters(old_ledger_sizes, old_projection_sizes, [new_node])
    waitNodeLedgersEquality(looper, new_node, *other_nodes)
    fill_counters(new_ledger_sizes, new_projection_sizes, [new_node])
    check_sizes([new_node])

    # Set the old counters to be current ledger and projection size
    fill_counters(old_ledger_sizes, old_projection_sizes, nodeSet)

    more_nyms_count = 5
    for tc, tw in trust_anchors:
        for i in range(more_nyms_count):
            non_privileged.append(getClientAddedWithRole(other_nodes,
                                                         tdirWithPoolTxns,
                                                         looper,
                                                         tc, tw,
                                                         'NP1' + str(i)))

    # The new node should process transactions done by Nyms added to its
    # ledger while catchup
    fill_counters(new_ledger_sizes, new_projection_sizes, nodeSet)
    new_txn_count = more_nyms_count*len(trust_anchors)
    check_sizes(nodeSet)
