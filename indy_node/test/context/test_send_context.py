import json

import pytest
from plenum.common.constants import DATA, META

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
#from indy_common.config import SCHEMA_ATTRIBUTES_LIMIT
from indy_common.constants import CONTEXT_NAME, CONTEXT_VERSION, CONTEXT_CONTEXT, RS_TYPE, CONTEXT_TYPE
from indy_node.test.context.helper import W3C_BASE_CONTEXT
from indy_common.types import SetContextField
from indy_node.test.api.helper import validate_write_reply, sdk_write_context_and_check
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT


def test_send_context_pass(looper, sdk_pool_handle,
                                     sdk_wallet_endorser):
    rep = sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        W3C_BASE_CONTEXT,
        "Base_Context",
        "1.0"
    )
    meta = rep[0][0]['operation'][META]
    assert meta[CONTEXT_VERSION] == '1.0'
    assert meta[CONTEXT_NAME] == 'Base_Context'
    assert meta[RS_TYPE] == CONTEXT_TYPE
    data = rep[0][0]['operation'][DATA]
    assert data == W3C_BASE_CONTEXT


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
