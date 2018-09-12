import shutil

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.util import randomString
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data, \
    waitNodeDataEquality
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.test_node import checkNodesConnected, ensure_node_disconnected
from indy_common.constants import TRUST_ANCHOR_STRING
from indy_common.config_helper import NodeConfigHelper
from indy_node.test.helper import TestNode, sdk_add_raw_attribute

TestRunningTimeLimitSec = 200


def test_state_regenerated_from_ledger(looper,
                                       nodeSet, tconf, tdir,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       allPluginsPath):
    """
    Node loses its state database but recreates it from ledger after start.
    Checking ATTRIB txns too since they store some data off ledger too
    """
    trust_anchors = []
    for i in range(5):
        trust_anchors.append(sdk_add_new_nym(looper, sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             'TA' + str(i),
                                             TRUST_ANCHOR_STRING))
        sdk_add_raw_attribute(looper, sdk_pool_handle,
                              trust_anchors[-1],
                              randomString(6),
                              randomString(10))

    for wh in trust_anchors:
        for i in range(3):
            sdk_add_new_nym(looper, sdk_pool_handle,
                            wh, 'NP1' + str(i))

    ensure_all_nodes_have_same_data(looper, nodeSet)

    node_to_stop = nodeSet[-1]
    node_state = node_to_stop.states[DOMAIN_LEDGER_ID]
    assert not node_state.isEmpty
    state_db_path = node_state._kv.db_path
    node_to_stop.cleanupOnStopping = False
    node_to_stop.stop()
    looper.removeProdable(node_to_stop)
    ensure_node_disconnected(looper, node_to_stop, nodeSet[:-1])

    shutil.rmtree(state_db_path)

    config_helper = NodeConfigHelper(node_to_stop.name, tconf, chroot=tdir)
    restarted_node = TestNode(
        node_to_stop.name,
        config_helper=config_helper,
        config=tconf,
        pluginPaths=allPluginsPath,
        ha=node_to_stop.nodestack.ha,
        cliha=node_to_stop.clientstack.ha)
    looper.add(restarted_node)
    nodeSet[-1] = restarted_node

    looper.run(checkNodesConnected(nodeSet))
    # Need some time as `last_ordered_3PC` is compared too and that is
    # communicated through catchup
    waitNodeDataEquality(looper, restarted_node, *nodeSet[:-1])

    # Pool is still functional
    for wh in trust_anchors:
        sdk_add_new_nym(looper, sdk_pool_handle,
                        wh, 'NP--' + randomString(5))

    ensure_all_nodes_have_same_data(looper, nodeSet)
