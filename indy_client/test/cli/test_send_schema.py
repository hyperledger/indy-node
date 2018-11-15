import pytest

from indy_node.test.api.helper import sdk_write_schema, validate_write_reply
from plenum.test.helper import sdk_check_reply
from plenum.common.exceptions import OperationError


def test_send_schema_multiple_attrib(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    req_resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1", "attrib2", "attrib3"],
                                "faber", "1.4")
    sdk_check_reply(req_resp)


def test_send_schema_one_attrib(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    req_resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1"],
                                "University of Saber", "1.0")
    sdk_check_reply(req_resp)


def test_can_not_send_same_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor):
    sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor, ["attrib1", "attrib2", "attrib3"],
                     "business", "1.8")

    with pytest.raises(OperationError) as ex_info:
        req_resp = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor,
                                    ["attrib1", "attrib2", "attrib3"], "business2", "1.8")
        validate_write_reply(req_resp[1])
        ex_info.match("can have one and only one SCHEMA with name business and version 1.8")