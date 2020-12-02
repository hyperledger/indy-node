from indy_common.config_helper import NodeConfigHelper
from indy_node.test.conftest import sdk_node_theta_added
from indy_node.test.helper import TestNode
from plenum.test.test_node import ensureElectionsDone

from plenum.common.util import randomString, hexToFriendly
from plenum.common.constants import SERVICES, TARGET_NYM, DATA
from plenum.common.txn_util import get_payload_data
from plenum.test.helper import waitForViewChange

from plenum.test.pool_transactions.helper import demote_node, promote_node

nodeCount = 7


def testSuspendNode(looper, sdk_pool_handle, sdk_wallet_trustee, nodeSet,
                    tdir, tconf, allPluginsPath):
    """
    Suspend a node and then cancel suspension. Suspend while suspended
    to test that there is no error
    """
    start_view_no = nodeSet[0].viewNo
    new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                        nodeSet,
                                                        tdir,
                                                        tconf,
                                                        sdk_pool_handle,
                                                        sdk_wallet_trustee,
                                                        allPluginsPath,
                                                        node_config_helper_class=NodeConfigHelper,
                                                        testNodeClass=TestNode,
                                                        name="Node-" + randomString(5))
    waitForViewChange(looper=looper, txnPoolNodeSet=nodeSet,
                      expectedViewNo=start_view_no + 1)
    ensureElectionsDone(looper=looper, nodes=nodeSet)

    demote_node(looper, sdk_wallet_trustee, sdk_pool_handle, new_node)
    _wait_view_change_finish(looper, nodeSet[:-1], start_view_no + 1)

    demote_node(looper, sdk_wallet_trustee, sdk_pool_handle, new_node)

    promote_node(looper, sdk_wallet_trustee, sdk_pool_handle, new_node)
    _wait_view_change_finish(looper, nodeSet[:-1], start_view_no + 2)

    promote_node(looper, sdk_wallet_trustee, sdk_pool_handle, new_node)


def _wait_view_change_finish(looper, nodes, view_no):
    waitForViewChange(looper=looper, txnPoolNodeSet=nodes,
                      expectedViewNo=view_no)
    ensureElectionsDone(looper=looper, nodes=nodes)


def testDemoteNodeWhichWasNeverActive(looper, nodeSet, sdk_pool_handle,
                                      sdk_wallet_trustee, tdir, tconf,
                                      allPluginsPath):
    """
    Add a node without services field and check that the ledger does not
    contain the `services` field and check that it can be demoted and
    the ledger has `services` as empty list
    """
    new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                        nodeSet,
                                                        tdir,
                                                        tconf,
                                                        sdk_pool_handle,
                                                        sdk_wallet_trustee,
                                                        allPluginsPath,
                                                        node_config_helper_class=NodeConfigHelper,
                                                        testNodeClass=TestNode,
                                                        name="Node-" + randomString(5),
                                                        services=None)

    looper.runFor(tconf.PROPAGATE_REQUEST_DELAY * 1.5)
    for node in nodeSet[:nodeCount]:
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        txn_data = get_payload_data(txn)
        assert txn_data[TARGET_NYM] == hexToFriendly(new_node.nodestack.verhex)
        assert SERVICES not in txn_data[DATA]

    demote_node(looper, new_steward_wallet, sdk_pool_handle, new_node)

    for node in nodeSet[:nodeCount]:
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        txn_data = get_payload_data(txn)
        assert txn_data[TARGET_NYM] == hexToFriendly(new_node.nodestack.verhex)
        assert SERVICES in txn_data[DATA] and txn_data[DATA][SERVICES] == []
