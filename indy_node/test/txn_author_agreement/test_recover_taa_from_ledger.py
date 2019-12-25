from plenum.common.constants import TXN_AUTHOR_AGREEMENT, TXN_AUTHOR_AGREEMENT_DIGEST, \
    TXN_AUTHOR_AGREEMENT_RATIFICATION_TS, TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_RETIREMENT_TS, \
    CURRENT_TXN_PAYLOAD_VERSIONS
import time

from indy_node.test.helper import start_stopped_node
from plenum.common.txn_util import get_txn_time
from plenum.common.util import randomString, get_utc_epoch
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected
from plenum.test.txn_author_agreement.helper import sdk_send_txn_author_agreement, sdk_get_txn_author_agreement, \
    sdk_send_txn_author_agreement_disable


def test_recover_taa_from_ledger(txnPoolNodeSet,
                                 sdk_pool_handle,
                                 sdk_wallet_trustee,
                                 looper,
                                 monkeypatch,
                                 setup_aml,
                                 tconf,
                                 tdir,
                                 allPluginsPath):
    orig_handlers = {}
    # Step 1. Stop one node
    node_to_stop = txnPoolNodeSet[-1]
    rest_pool = txnPoolNodeSet[:-1]
    disconnect_node_and_ensure_disconnected(looper,
                                            txnPoolNodeSet,
                                            node_to_stop.name,
                                            stopNode=True)
    looper.removeProdable(name=node_to_stop.name)

    # Step 2. Patch all the rest nodes for using old version TAA handler

    # it's ugly but it works
    globals()['CURRENT_TXN_PAYLOAD_VERSIONS'][TXN_AUTHOR_AGREEMENT] = '1'
    for node in rest_pool:
        handler = node.write_manager.request_handlers.get(TXN_AUTHOR_AGREEMENT)[0]
        orig_handlers[node.name] = handler
        handler_for_v_1 = node.write_manager._request_handlers_with_version.get((TXN_AUTHOR_AGREEMENT, "1"))[0]
        node.write_manager.request_handlers[TXN_AUTHOR_AGREEMENT] = [handler_for_v_1]

    # Step 3. Send TAA txn in old way
    text = randomString(1024)
    version_0 = randomString(16)
    res = sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_0, text)[1]
    taa_0_ratification_ts = get_txn_time(res['result'])

    version_1 = randomString(16)
    res = sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_1, text)[1]
    taa_1_ratification_ts = get_txn_time(res['result'])

    # Step 4. return original TAA handlers back

    # it's ugly but it works
    globals()['CURRENT_TXN_PAYLOAD_VERSIONS'][TXN_AUTHOR_AGREEMENT] = '2'
    for node in rest_pool:
        node.write_manager.request_handlers[TXN_AUTHOR_AGREEMENT] = [orig_handlers[node.name]]

    # Step 5. Send another TAA txn in new way without optional parameters
    text_2 = randomString(1024)
    version_2 = randomString(16)
    ratified_2 = get_utc_epoch() - 300
    res_0 = sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee,
                                          version_2, text_2, ratified=ratified_2)[1]

    # Step 6. Send another TAA txn in new way without optional parameter
    text = randomString(1024)
    version_3 = randomString(16)
    ratified_3 = get_utc_epoch() - 300
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_3, text, ratified=ratified_3)

    # Step 7. Send taa updating for the second taa transaction (for checking txn with optional parameter)
    retired_time = int(time.time()) + 20
    retired_time_in_past = int(time.time()) - 20
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_2, retired=retired_time)

    # Step 8. Ensure, that all TAAs was written
    res_1 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_1)[1]
    assert TXN_AUTHOR_AGREEMENT_DIGEST not in res_1['result']['data']
    assert TXN_AUTHOR_AGREEMENT_RATIFICATION_TS not in res_1['result']['data']
    assert res_1['result']['data'][TXN_AUTHOR_AGREEMENT_VERSION] == version_1

    res_2 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_2)[1]
    check_result_contains_expected_taa_data(res_2, version_2, ratified_2, retired_time)

    res_3 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_3)[1]
    check_result_contains_expected_taa_data(res_3, version_3, ratified_3)

    # Step 9. Return previous disconnected node back
    node_to_stop = start_stopped_node(node_to_stop, looper,
                                      tconf, tdir, allPluginsPath)
    txnPoolNodeSet = rest_pool + [node_to_stop]

    # Step 10. Ensure that all nodes have the same data
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)

    # Step 11. Send another taa txns for checking pool writability
    text = randomString(1024)
    version_4 = randomString(16)
    ratified_4 = get_utc_epoch() - 300
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_4, text, ratified=ratified_4)

    # Step 12. Ensure that all nodes have the same data
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)

    # Step 13. Retire TAA written using old handler, make sure ratification date is not spoiled
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version_1, retired=retired_time_in_past)
    res_1 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_1)[1]
    check_result_contains_expected_taa_data(res_1, version_1, taa_1_ratification_ts, retired_time_in_past)

    # Step 14. Disable TAAs written using old handler, make sure ratification date is not spoiled
    disable_res = sdk_send_txn_author_agreement_disable(looper, sdk_pool_handle, sdk_wallet_trustee)[1]

    res_0 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_0)[1]
    check_result_contains_expected_taa_data(res_0, version_0, taa_0_ratification_ts, get_txn_time(disable_res['result']))

    res_1 = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, version=version_1)[1]
    check_result_contains_expected_taa_data(res_1, version_1, taa_1_ratification_ts, retired_time_in_past)


def check_result_contains_expected_taa_data(result, version, ratification_ts, retired_time=None):
    assert TXN_AUTHOR_AGREEMENT_DIGEST in result['result']['data']
    assert TXN_AUTHOR_AGREEMENT_RATIFICATION_TS in result['result']['data']
    assert result['result']['data'][TXN_AUTHOR_AGREEMENT_VERSION] == version
    assert result['result']['data'][TXN_AUTHOR_AGREEMENT_RATIFICATION_TS] == ratification_ts
    if retired_time:
        assert result['result']['data'][TXN_AUTHOR_AGREEMENT_RETIREMENT_TS] == retired_time
    else:
        assert TXN_AUTHOR_AGREEMENT_RETIREMENT_TS not in result['result']['data']

