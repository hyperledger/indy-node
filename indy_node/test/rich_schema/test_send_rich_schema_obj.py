import json
import random

import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_CONTEXT_TYPE_VALUE, JSON_LD_CONTEXT, RS_SCHEMA_TYPE_VALUE, \
    RS_MAPPING_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA, RICH_SCHEMA_ENCODING, \
    RICH_SCHEMA_MAPPING, RICH_SCHEMA_CRED_DEF, RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE
from indy_node.test.api.helper import sdk_write_rich_schema_object_and_check, \
    sdk_build_rich_schema_request
from indy_node.test.rich_schema.templates import W3C_BASE_CONTEXT, RICH_SCHEMA_EX1
from plenum.common.constants import TXN_PAYLOAD_METADATA_REQ_ID
from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.common.types import OPERATION
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, randomString())])
def test_send_rich_schema_obj(looper, sdk_pool_handle, sdk_wallet_endorser,
                              txn_type, rs_type, content):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, randomString())])
def test_write_same_object_returns_same_response(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                 txn_type, rs_type, content):
    request = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                            txn_type, rs_id=randomString(), rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
    rep1 = sdk_get_and_check_replies(looper, [req])

    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
    rep2 = sdk_get_and_check_replies(looper, [req])

    assert rep1 == rep2


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString())])
def test_write_same_object_with_different_reqid_fails(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                      txn_type, rs_type, content):
    request1 = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                             txn_type, rs_id=randomString(), rs_name=randomString(),
                                             rs_version='1.0', rs_type=rs_type,
                                             rs_content=json.dumps(content))
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request1)
    sdk_get_and_check_replies(looper, [req])

    request2 = json.loads(request1)
    request2[TXN_PAYLOAD_METADATA_REQ_ID] = random.randint(10, 1000000000)
    request2 = json.dumps(request2)

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request2)
        sdk_get_and_check_replies(looper, [req])


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString()),
                          (RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, randomString())])
@pytest.mark.parametrize('missing_field',
                         ["id", "rsName", "rsVersion", "content", "rsType"])
def test_validate_fail_missing_fields(looper, sdk_pool_handle, sdk_wallet_endorser,
                                      txn_type, rs_type, content, missing_field):
    request = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                            txn_type, rs_id=randomString(), rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))
    request = json.loads(request)
    request[OPERATION].pop(missing_field, None)
    request = json.dumps(request)

    with pytest.raises(RequestNackedException, match='missed fields'):
        req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)
        sdk_get_and_check_replies(looper, [req])
