import json

import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
#from indy_common.config import SCHEMA_ATTRIBUTES_LIMIT
from indy_common.constants import CONTEXT_NAME, CONTEXT_VERSION, CONTEXT_CONTEXT_ARRAY
from indy_common.types import SetContextField
from indy_node.test.api.helper import validate_write_reply, sdk_write_context_and_check
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT


def test_send_context_multiple_links_with_object(looper, sdk_pool_handle,
                                     sdk_wallet_endorser):
    test_context_object = {
        "name": "did:sov:11111111111111111111111;content-id=ctx:UVj5w8DRzcmPVDpUMr4AZhJ",
        "address": "did:sov:11111111111111111111111;content-id=ctx:UVj5w8DRzcmPVDpUMr4AZhJ"
    }
    sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        [
            "did:sov:11111111111111111111111;content-id=ctx:UVj5w8DRzcmPVDpUMr4AZhJ",
            "did:sov:11111111111111111111111;content-id=ctx:AZKWUJ3zArXPG36kyTJZZm",
            "did:sov:11111111111111111111111;content-id=ctx:9TDvb9PPgKQUWNQcWAFMo4",
            test_context_object
        ],
        "ISO18013_DriverLicenseContextr",
        "1.9"
    )

def test_send_context_multiple_links(looper, sdk_pool_handle,
                                     sdk_wallet_trustee):
    sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trustee,
        [
            "did:sov:11111111111111111111111;content-id=ctx:UVj5w8DRzcmPVDpUMr4AZhJ",
            "did:sov:11111111111111111111111;content-id=ctx:AZKWUJ3zArXPG36kyTJZZm",
            "did:sov:11111111111111111111111;content-id=ctx:9TDvb9PPgKQUWNQcWAFMo4"
        ],
        "ISO18013_DriverLicenseContext",
        "1.9"
    )


def test_send_context_one_link(looper, sdk_pool_handle,
                                sdk_wallet_trustee):
    sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_trustee,
        [
            "did:sov:11111111111111111111111;content-id=ctx:9TDvb9PPgKQUWNQcWAFMo4"
        ],
        "ISO18013_DriverLicenseContext2",
        "1.9"
    )

'''
def test_can_not_send_same_schema(looper, sdk_pool_handle,
                                  sdk_wallet_endorser):
    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        ["attrib1", "attrib2", "attrib3"],
        "business",
        "1.8"
    )

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        resp = sdk_write_schema_and_check(
            looper, sdk_pool_handle,
            sdk_wallet_endorser,
            ["attrib1", "attrib2", "attrib3"],
            "business",
            "1.8"
        )
        validate_write_reply(resp)


def test_schema_maximum_attrib(looper, sdk_pool_handle,
                               sdk_wallet_endorser):
    attribs = []
    for i in range(SCHEMA_ATTRIBUTES_LIMIT):
        attribs.append(randomString(NAME_FIELD_LIMIT))

    sdk_write_schema_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
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
    '''
