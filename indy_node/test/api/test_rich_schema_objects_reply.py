import json

import pytest

from indy_common.constants import JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, RICH_SCHEMA, RICH_SCHEMA_ENCODING, \
    RICH_SCHEMA_MAPPING, RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, \
    RS_ENCODING_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE
from indy_node.test.api.helper import validate_write_reply, validate_rich_schema_txn, sdk_build_rich_schema_request
from indy_node.test.rich_schema.templates import RICH_SCHEMA_EX1, W3C_BASE_CONTEXT
from plenum.common.util import randomString
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, randomString())])
def test_rich_schema_object_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward,
                                           txn_type, rs_type, content):
    request = sdk_build_rich_schema_request(looper, sdk_wallet_steward,
                                            txn_type, rs_id=randomString(), rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]

    validate_write_reply(reply)
    validate_rich_schema_txn(reply['result']['txn'], txn_type)
