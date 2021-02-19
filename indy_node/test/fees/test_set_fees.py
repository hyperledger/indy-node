from indy_common.constants import SET_FEES, FEE, FEES
from indy_node.test.fees.helper import sdk_set_fees, sdk_get_fees, sdk_get_fee


def test_set_fees(looper, sdk_pool_handle, nodeSet,
                  sdk_wallet_trustee, monkeypatch):
    txn_alias = "txn_alias"
    fee_value = 4

    for n in nodeSet:
        handler = n.write_manager.request_handlers.get(SET_FEES)[0]
        monkeypatch.setattr(handler, 'static_validation', lambda _: _)
        monkeypatch.setattr(handler, 'additional_dynamic_validation', lambda a, b: 0)

    sdk_set_fees(looper, sdk_pool_handle, sdk_wallet_trustee, {txn_alias: fee_value})
    get_fees_result = sdk_get_fees(looper, sdk_pool_handle, sdk_wallet_trustee)
    get_fee_result = sdk_get_fee(looper, sdk_pool_handle, sdk_wallet_trustee, txn_alias)

    assert get_fees_result[1]["result"][FEES] == {txn_alias: fee_value}
    assert get_fee_result[1]["result"][FEE] == fee_value
