import sys

from indy.ledger import build_nym_request

from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy_node.test.helper import start_stopped_node
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.test.delayers import cDelay
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_reply
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected


def create_nym_request(looper, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()
    _, identifier = sdk_wallet_steward
    return looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))


def test_node_crashed_while_writing_nym(looper, nodeSet, tconf, tdir, allPluginsPath,
                                        sdk_pool_handle, sdk_wallet_steward):
    '''
    The Node has some uncommitted domain state while writing NYMs
    and crashed.
    Make sure that it can continue ordering when go up again.
    '''
    good_node = nodeSet[0]
    crashed_node = nodeSet[-1]
    crashed_node.nodeIbStasher.delay(cDelay(sys.maxsize))

    # 1. send a request so that it's applied  but not ordered on Node4
    # while ordered on others
    request1 = create_nym_request(looper, sdk_wallet_steward)
    sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request1))
    crashed_uncommitted_before = crashed_node.getState(DOMAIN_LEDGER_ID).headHash
    crashed_committed_before = crashed_node.getState(DOMAIN_LEDGER_ID).committedHeadHash
    assert crashed_uncommitted_before == good_node.getState(DOMAIN_LEDGER_ID).headHash
    assert crashed_committed_before != good_node.getState(DOMAIN_LEDGER_ID).committedHeadHash

    # 2. simulate crashing of Node4 with uncommitted state
    crashed_node.cleanupOnStopping = False
    disconnect_node_and_ensure_disconnected(looper, nodeSet, crashed_node.name)
    looper.removeProdable(crashed_node)
    crashed_node = start_stopped_node(crashed_node, looper, tconf, tdir, allPluginsPath)
    nodeSet[-1] = crashed_node

    # 3. make sure that crashed node can continue ordering
    request2 = create_nym_request(looper, sdk_wallet_steward)
    sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request2))
    ensure_all_nodes_have_same_data(looper, nodeSet)
