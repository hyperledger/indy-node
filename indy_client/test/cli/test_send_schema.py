from indy_node.test.api.helper import sdk_write_schema
from plenum.test.helper import sdk_check_reply


def test_send_schema_multiple_attrib(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    _, resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1", "attrib2", "attrib3"])
    sdk_check_reply(resp)


def test_send_schema_one_attrib(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    _, resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1"])
    sdk_check_reply(resp)


def test_can_not_send_same_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1", "attrib2", "attrib3"])
    _, resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1", "attrib2", "attrib3"])
    not sdk_check_reply(resp)