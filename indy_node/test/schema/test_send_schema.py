import json

import pytest

from indy_common.config import SCHEMA_ATTRIBUTES_LIMIT
from indy_common.constants import SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES
from indy_common.types import SchemaField
from indy_node.test.api.helper import validate_write_reply, sdk_write_schema_and_check
from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT


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


def test_schema_maximum_attrib(looper, sdk_pool_handle,
                               sdk_wallet_trust_anchor):
    attribs = []
    for i in range(SCHEMA_ATTRIBUTES_LIMIT):
        attribs.append(randomString(NAME_FIELD_LIMIT))

    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trust_anchor,
        attribs,
        "business1",
        "1.9"
    )


def test_schema_over_maximum_attrib():
    attribs = []
    for i in range(SCHEMA_ATTRIBUTES_LIMIT + 1):
        attribs.append('attrib' + str(i))

    schema = SchemaField()
    with pytest.raises(Exception) as ex_info:
        schema.validate({SCHEMA_NAME: "business2",
                         SCHEMA_VERSION: "2.0",
                         SCHEMA_ATTR_NAMES: attribs})
    ex_info.match(
        "length should be at most {}".format(SCHEMA_ATTRIBUTES_LIMIT)
    )
