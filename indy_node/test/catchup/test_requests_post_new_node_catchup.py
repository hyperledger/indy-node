from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.types import f
from plenum.common.util import randomString
from plenum.test.helper import assertLength
from plenum.test.node_catchup.helper import checkNodeDataForEquality, \
    waitNodeDataEquality
from plenum.test.test_node import ensure_node_disconnected, checkNodesConnected
from indy_client.test.client.TestClient import TestClient
from indy_client.test.helper import getClientAddedWithRole
from indy_common.constants import TRUST_ANCHOR
from indy_node.test.conftest import nodeThetaAdded
from indy_node.test.helper import TestNode, addRawAttribute, getAttribute
from indy_common.config_helper import NodeConfigHelper


def test_new_node_catchup_update_projection(looper, tdirWithClientPoolTxns,
                                            tdirWithDomainTxnsUpdated,
                                            nodeSet, tconf, tdir,
                                            trustee, trusteeWallet,
                                            allPluginsPath,
                                            some_transactions_done
                                            ):
    """
    A node which receives txns from catchup updates both ledger and projection
    4 nodes start up and some txns happen, after txns are done, new node joins
    and starts catching up, the node should not process requests while catchup
    is in progress. Make sure the new requests are coming from the new NYMs
    added while the node was offline or catching up.
    """
    # Create a new node and stop it.

    new_steward, new_steward_wallet, new_node = nodeThetaAdded(looper,
                                                               nodeSet,
                                                               tdirWithClientPoolTxns,
                                                               tconf, trustee,
                                                               trusteeWallet,
                                                               allPluginsPath,
                                                               TestNode,
                                                               TestClient,
                                                               NodeConfigHelper,
                                                               tdir)

    waitNodeDataEquality(looper, new_node, *nodeSet[:-1])
    ta_count = 2
    np_count = 2
    new_txn_count = 2 * ta_count + np_count   # Since ATTRIB txn is done for TA
    old_ledger_sizes = {}
    new_ledger_sizes = {}
    old_projection_sizes = {}
    new_projection_sizes = {}
    old_seq_no_map_sizes = {}
    new_seq_no_map_sizes = {}

    def get_ledger_size(node):
        return len(node.domainLedger)

    def get_projection_size(node):
        domain_state = node.getState(DOMAIN_LEDGER_ID)
        return len(domain_state.as_dict)

    def get_seq_no_map_size(node):
        return node.seqNoDB.size

    def fill_counters(ls, ps, ss, nodes):
        for n in nodes:
            ls[n.name] = get_ledger_size(n)
            ps[n.name] = get_projection_size(n)
            ss[n.name] = get_seq_no_map_size(n)

    def check_sizes(nodes):
        for node in nodes:
            assert new_ledger_sizes[node.name] - \
                old_ledger_sizes[node.name] == new_txn_count
            assert new_projection_sizes[node.name] - \
                old_projection_sizes[node.name] == new_txn_count
            assert new_seq_no_map_sizes[node.name] - \
                old_seq_no_map_sizes[node.name] == new_txn_count

    # Stop a node and note down the sizes of ledger and projection (state)
    other_nodes = nodeSet[:-1]
    fill_counters(old_ledger_sizes, old_projection_sizes, old_seq_no_map_sizes,
                  other_nodes)
    new_node.cleanupOnStopping = False
    new_node.stop()
    looper.removeProdable(new_node)
    ensure_node_disconnected(looper, new_node, other_nodes)

    trust_anchors = []
    attributes = []
    for i in range(ta_count):
        trust_anchors.append(
            getClientAddedWithRole(
                other_nodes,
                tdirWithClientPoolTxns,
                looper,
                trustee,
                trusteeWallet,
                'TA' + str(i),
                role=TRUST_ANCHOR,
                client_connects_to=len(other_nodes)))
        attributes.append((randomString(6), randomString(10)))
        addRawAttribute(looper, *trust_anchors[-1], *attributes[-1],
                        dest=trust_anchors[-1][1].defaultId)
    non_privileged = []
    for i in range(np_count):
        non_privileged.append(
            getClientAddedWithRole(
                other_nodes,
                tdirWithClientPoolTxns,
                looper,
                trustee,
                trusteeWallet,
                'NP' + str(i),
                client_connects_to=len(other_nodes)))

    checkNodeDataForEquality(nodeSet[0], *other_nodes)
    fill_counters(new_ledger_sizes, new_projection_sizes, new_seq_no_map_sizes,
                  other_nodes)
    # The size difference should be same as number of new NYM txns
    check_sizes(other_nodes)

    config_helper = NodeConfigHelper(new_node.name, tconf, chroot=tdir)
    new_node = TestNode(
        new_node.name,
        config_helper=config_helper,
        config=tconf,
        pluginPaths=allPluginsPath,
        ha=new_node.nodestack.ha,
        cliha=new_node.clientstack.ha)
    looper.add(new_node)
    nodeSet[-1] = new_node
    fill_counters(old_ledger_sizes, old_projection_sizes, old_seq_no_map_sizes,
                  [new_node])
    looper.run(checkNodesConnected(nodeSet))
    waitNodeDataEquality(looper, new_node, *other_nodes)
    fill_counters(new_ledger_sizes, new_projection_sizes, new_seq_no_map_sizes,
                  [new_node])
    check_sizes([new_node])

    for i, (tc, tw) in enumerate(trust_anchors):
        # To prevent sending of 'get_attr' to just one node
        tc._read_only_requests = set()

        reply = getAttribute(looper, tc, tw, tw.defaultId, *attributes[i])
        all_replies = tc.getRepliesFromAllNodes(reply[f.IDENTIFIER.nm],
                                                reply[f.REQ_ID.nm])
        assertLength(all_replies, len(nodeSet))
        assert new_node.clientstack.name in all_replies

    # Set the old counters to be current ledger and projection size
    fill_counters(old_ledger_sizes, old_projection_sizes, old_seq_no_map_sizes,
                  nodeSet)

    more_nyms_count = 2
    for tc, tw in trust_anchors:
        for i in range(more_nyms_count):
            non_privileged.append(getClientAddedWithRole(other_nodes,
                                                         tdirWithClientPoolTxns,
                                                         looper,
                                                         tc, tw,
                                                         'NP1' + str(i)))

    # The new node should process transactions done by Nyms added to its
    # ledger while catchup
    fill_counters(new_ledger_sizes, new_projection_sizes, new_seq_no_map_sizes,
                  nodeSet)
    new_txn_count = more_nyms_count * len(trust_anchors)
    check_sizes(nodeSet)
