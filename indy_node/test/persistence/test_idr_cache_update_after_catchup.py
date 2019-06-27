import json

from indy.ledger import build_nym_request, sign_request, submit_request

from indy_common.state import domain
from indy_node.test.helper import start_stopped_node, createHalfKeyIdentifierAndAbbrevVerkey
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.txn_util import get_txn_time
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected


def test_idr_cache_update_after_catchup(txnPoolNodeSet,
                                        looper,
                                        sdk_pool_handle,
                                        sdk_wallet_steward,
                                        tconf,
                                        tdir,
                                        allPluginsPath):
    wallet_handle, identifier = sdk_wallet_steward
    node_to_disconnect = txnPoolNodeSet[-1]
    disconnect_node_and_ensure_disconnected(looper,
                                            txnPoolNodeSet,
                                            node_to_disconnect.name,
                                            stopNode=True)
    looper.removeProdable(node_to_disconnect)

    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()
    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    restarted_node = start_stopped_node(node_to_disconnect, looper,
                                        tconf, tdir, allPluginsPath)
    txnPoolNodeSet[-1] = restarted_node
    waitNodeDataEquality(looper, restarted_node, *txnPoolNodeSet[:-1])
    root_hash = restarted_node.db_manager.ts_store.get_equal_or_prev(get_txn_time(result['result']))
    key = domain.make_state_path_for_nym(idr)
    from_state = restarted_node.getState(DOMAIN_LEDGER_ID).get_for_root_hash(root_hash=root_hash,
                                                                                   key=key)
    assert from_state
    deserialized = restarted_node.write_manager.state_serializer.deserialize(from_state)
    assert deserialized
    items_after = restarted_node.db_manager.idr_cache.get(idr)
    assert items_after
