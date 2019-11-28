from plenum.test.test_node import ensureElectionsDone

from plenum.common.util import randomString, hexToFriendly
from plenum.common.constants import SERVICES, TARGET_NYM, DATA
from plenum.common.txn_util import get_payload_data
from plenum.test.helper import waitForViewChange

from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_add_new_node, demote_node, promote_node


def testSuspendNode(looper, sdk_pool_handle, sdk_wallet_trustee, newNodeAdded, nodeSet):
    """
    Suspend a node and then cancel suspension. Suspend while suspended
    to test that there is no error
    """
    start_view_no = nodeSet[0].viewNo
    new_steward_wallet, new_node = newNodeAdded

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
    alias = randomString(5)
    new_node_name = "Node-" + alias
    sdk_wallet_steward = sdk_add_new_nym(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         alias="Steward-" + alias,
                                         role='STEWARD')
    new_node = sdk_add_new_node(looper,
                                sdk_pool_handle,
                                sdk_wallet_steward,
                                new_node_name,
                                tdir,
                                tconf,
                                allPluginsPath,
                                services=None)

    looper.runFor(tconf.PROPAGATE_REQUEST_DELAY * 1.5)
    for node in nodeSet:
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        txn_data = get_payload_data(txn)
        assert txn_data[TARGET_NYM] == hexToFriendly(new_node.nodestack.verhex)
        assert SERVICES not in txn_data[DATA]

    demote_node(looper, sdk_wallet_steward, sdk_pool_handle, new_node)

    for node in nodeSet:
        txn = [t for _, t in node.poolLedger.getAllTxn()][-1]
        txn_data = get_payload_data(txn)
        assert txn_data[TARGET_NYM] == hexToFriendly(new_node.nodestack.verhex)
        assert SERVICES in txn_data[DATA] and txn_data[DATA][SERVICES] == []
