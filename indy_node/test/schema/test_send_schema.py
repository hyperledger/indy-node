import pytest

from indy_node.test.api.helper import validate_write_reply, sdk_write_schema_and_check
from plenum.common.exceptions import RequestRejectedException


def test_send_schema_multiple_attrib(looper, sdk_pool_handle,
                                     sdk_wallet_trust_anchor):
    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        ["attrib1", "attrib2", "attrib3"],
        "faber",
        "1.4"
    )


def test_send_schema_one_attrib(looper, sdk_pool_handle,
                                sdk_wallet_trust_anchor):
    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        ["attrib1"],
        "University of Saber",
        "1.0"
    )


def test_can_not_send_same_schema(looper, sdk_pool_handle,
                                  sdk_wallet_trust_anchor):
    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        ["attrib1", "attrib2", "attrib3"],
        "business",
        "1.8"
    )

    with pytest.raises(RequestRejectedException) as ex_info:
        resp = sdk_write_schema_and_check(
            looper, sdk_pool_handle,
            sdk_wallet_trust_anchor,
            ["attrib1", "attrib2", "attrib3"],
            "business",
            "1.8"
        )
        validate_write_reply(resp)
    ex_info.match(
        "can have one and only one SCHEMA with name business and version 1.8"
    )
