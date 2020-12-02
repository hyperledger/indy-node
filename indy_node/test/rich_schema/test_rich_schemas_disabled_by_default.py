import json

import pytest

from indy_common.constants import JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, RS_ID, GET_RICH_SCHEMA_OBJECT_BY_ID, \
    GET_RICH_SCHEMA_OBJECT_BY_METADATA, RS_NAME, RS_VERSION, RS_TYPE
from indy_node.test.api.helper import sdk_build_rich_schema_request, sdk_write_rich_schema_object_and_check
from indy_node.test.helper import rich_schemas_enabled_scope
from indy_node.test.rich_schema.templates import W3C_BASE_CONTEXT
from indy_node.test.rich_schema.test_send_get_rich_schema_obj import PARAMS
from indy_node.test.state_proof.helper import sdk_submit_operation_and_get_result
from plenum.common.constants import TXN_TYPE
from plenum.common.exceptions import RequestNackedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies


@pytest.fixture(scope='module')
def write_rich_schema(looper, sdk_pool_handle, sdk_wallet_endorser, tconf):
    with rich_schemas_enabled_scope(tconf):
        for txn_type, rs_type, content, rs_id, rs_name, rs_version in PARAMS:
            sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                                   txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                                   rs_version=rs_version, rs_type=rs_type, rs_content=content)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id',
                         [(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT, randomString())])
def test_send_rich_schema_obj_disabled_by_default(looper, sdk_pool_handle, sdk_wallet_endorser, txn_type, rs_type,
                                                  content, rs_id):
    request = sdk_build_rich_schema_request(looper, sdk_wallet_endorser,
                                            txn_type, rs_id=rs_id, rs_name=randomString(),
                                            rs_version='1.0', rs_type=rs_type,
                                            rs_content=json.dumps(content))

    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_endorser, request)

    with pytest.raises(RequestNackedException, match='RichSchema transactions are disabled'):
        sdk_get_and_check_replies(looper, [req])


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_id_disabled_by_default(looper, sdk_pool_handle, sdk_wallet_endorser, txn_type,
                                                            rs_type, content, rs_id, rs_name, rs_version,
                                                            write_rich_schema):
    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
        RS_ID: rs_id,
    }

    with pytest.raises(RequestNackedException, match='RichSchema queries are disabled'):
        sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                            sdk_wallet_endorser,
                                            get_rich_schema_by_id_operation)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_metadata_disabled_by_default(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                                  txn_type, rs_type, content, rs_id, rs_name,
                                                                  rs_version, write_rich_schema):
    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }

    with pytest.raises(RequestNackedException, match='RichSchema queries are disabled'):
        sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                            sdk_wallet_endorser,
                                            get_rich_schema_by_metadata_operation)
