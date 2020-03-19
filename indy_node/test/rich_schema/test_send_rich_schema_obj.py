import json
import random

import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_CONTEXT_TYPE_VALUE, JSON_LD_CONTEXT, RS_SCHEMA_TYPE_VALUE, \
    RS_MAPPING_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA, RICH_SCHEMA_ENCODING, \
    RICH_SCHEMA_MAPPING, RICH_SCHEMA_CRED_DEF, RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE
from indy_node.test.api.helper import sdk_write_rich_schema_object_and_check, \
    sdk_build_rich_schema_request
from indy_node.test.rich_schema.templates import W3C_BASE_CONTEXT, RICH_SCHEMA_EX1, RICH_SCHEMA_ENCODING_EX1, \
    RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_CRED_DEF_EX1, RICH_SCHEMA_PRES_DEF_EX1
from plenum.common.constants import TXN_PAYLOAD_METADATA_REQ_ID
from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.common.types import OPERATION
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies


# The order of creation is essential as some rich schema object reference others by ID
# Encoding's id must be equal to the one used in RICH_SCHEMA_MAPPING_EX1

@pytest.mark.parametrize('txn_type, rs_type, content, rs_id',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT, randomString()),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1, RICH_SCHEMA_EX1['@id']),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA_ENCODING_EX1, "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD"),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_MAPPING_EX1['@id']),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA_CRED_DEF_EX1, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, RICH_SCHEMA_PRES_DEF_EX1, RICH_SCHEMA_PRES_DEF_EX1['@id'])])
def test_send_rich_schema_obj(looper, sdk_pool_handle, sdk_wallet_endorser,
                              txn_type, rs_type, content, rs_id):
    # 1. check that write is successful
    request = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                            txn_type, rs_id=rs_id, rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
    rep1 = sdk_get_and_check_replies(looper, [req])

    # 2. check that sending the same request gets the same reply
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
    rep2 = sdk_get_and_check_replies(looper, [req])
    assert rep1 == rep2

    # 3. check that using a different reqId for the same request gets an error
    request2 = json.loads(request)
    request2[TXN_PAYLOAD_METADATA_REQ_ID] = random.randint(10, 1000000000)
    request2 = json.dumps(request2)

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request2)
        sdk_get_and_check_replies(looper, [req])


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT, randomString()),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1, RICH_SCHEMA_EX1['@id']),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA_ENCODING_EX1, "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD"),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_MAPPING_EX1['@id']),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA_CRED_DEF_EX1, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, RICH_SCHEMA_PRES_DEF_EX1, RICH_SCHEMA_PRES_DEF_EX1['@id'])])
@pytest.mark.parametrize('missing_field',
                         ["id", "rsName", "rsVersion", "content", "rsType"])
def test_validate_fail_missing_fields(looper, sdk_pool_handle, sdk_wallet_endorser,
                                      txn_type, rs_type, content, rs_id, missing_field):
    request = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                            txn_type, rs_id=rs_id, rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))
    request = json.loads(request)
    request[OPERATION].pop(missing_field, None)
    request = json.dumps(request)

    with pytest.raises(RequestNackedException, match='missed fields'):
        req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
        sdk_get_and_check_replies(looper, [req])
