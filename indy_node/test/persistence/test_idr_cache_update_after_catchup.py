import json

from indy.ledger import build_nym_request, sign_request, submit_request

from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy_common.state import domain
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected, \
    reconnect_node_and_ensure_connected


def test_idr_cache_update_after_catchup(txnPoolNodeSet,
                                        looper,
                                        sdk_pool_handle,
                                        sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward
    node_to_disconnect = txnPoolNodeSet[-1]
    req_handler = node_to_disconnect.getDomainReqHandler()
    disconnect_node_and_ensure_disconnected(looper,
                                            txnPoolNodeSet,
                                            node_to_disconnect.name,
                                            stopNode=False)
    looper.runFor(2)
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    reconnect_node_and_ensure_connected(looper, txnPoolNodeSet, node_to_disconnect.name)
    waitNodeDataEquality(looper, node_to_disconnect, *txnPoolNodeSet)
    key = domain.make_state_path_for_nym(idr)
    root_hash = req_handler.ts_store.get_equal_or_prev(result['result']['txnTime'])
    from_state = req_handler.state.get_for_root_hash(root_hash=root_hash,
                                                     key=key)
    assert from_state
    deserialized = req_handler.stateSerializer.deserialize(from_state)
    assert deserialized
    items_after = req_handler.idrCache.get(idr)
    assert items_after
