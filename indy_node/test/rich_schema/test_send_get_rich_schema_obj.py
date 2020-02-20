import pytest

from indy_common.constants import SET_JSON_LD_CONTEXT, SET_RICH_SCHEMA, SET_RICH_SCHEMA_ENCODING, \
    SET_RICH_SCHEMA_MAPPING, SET_RICH_SCHEMA_CRED_DEF, \
    RS_CONTEXT_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, \
    GET_RICH_SCHEMA_OBJECT_BY_ID, RS_ID, GET_RICH_SCHEMA_OBJECT_BY_METADATA, RS_NAME, RS_VERSION, RS_TYPE
from indy_node.test.api.helper import sdk_write_rich_schema_object_and_check
from indy_node.test.rich_schema.templates import RICH_SCHEMA_EX1, W3C_BASE_CONTEXT
from indy_node.test.state_proof.helper import check_valid_proof, sdk_submit_operation_and_get_result
from plenum.common.constants import TXN_TYPE
from plenum.common.exceptions import RequestNackedException
from plenum.common.util import randomString, SortedDict


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
def test_send_get_rich_schema_obj_by_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                        txn_type, rs_type, content):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
        RS_ID: rs_id,
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_rich_schema_by_id_operation)
    expected_data = SortedDict({
        'id': rs_id,
        'rsType': rs_type,
        'rsName': rs_name,
        'rsVersion': rs_version,
        'content': content,
        'from': sdk_wallet_endorser[1]
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo']
    assert result['txnTime']
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
def test_send_get_rich_schema_obj_by_metadata(looper, sdk_pool_handle, sdk_wallet_endorser, sdk_wallet_client,
                                              txn_type, rs_type, content):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_rich_schema_by_metadata_operation)
    expected_data = SortedDict({
        'id': rs_id,
        'rsType': rs_type,
        'rsName': rs_name,
        'rsVersion': rs_version,
        'content': content,
        'from': sdk_wallet_endorser[1]
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo']
    assert result['txnTime']
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
def test_send_get_rich_schema_obj_by_invalid_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                txn_type, rs_type, content):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
        RS_ID: randomString(),
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_rich_schema_by_id_operation)
    assert result['data'] is None
    assert result['seqNo'] is None
    assert result['txnTime'] is None
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
@pytest.mark.parametrize('invalid_meta', [RS_NAME, RS_VERSION, RS_TYPE])
def test_send_get_rich_schema_obj_by_invalid_metadata(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                      txn_type, rs_type, content,
                                                      invalid_meta):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }
    get_rich_schema_by_metadata_operation[invalid_meta] = randomString()

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_rich_schema_by_metadata_operation)
    assert result['data'] is None
    assert result['seqNo'] is None
    assert result['txnTime'] is None
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
def test_send_get_rich_schema_obj_by_no_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                           txn_type, rs_type, content):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
    }

    with pytest.raises(RequestNackedException, match='missed fields'):
        sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                            sdk_wallet_endorser,
                                            get_rich_schema_by_id_operation)


@pytest.mark.parametrize('txn_type, rs_type, content',
                         [(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT),
                          (SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1),
                          (SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, randomString()),
                          (SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, randomString())])
@pytest.mark.parametrize('absent_meta', [RS_NAME, RS_VERSION, RS_TYPE])
def test_send_get_rich_schema_obj_by_no_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                           txn_type, rs_type, content,
                                           absent_meta):
    rs_id = randomString()
    rs_name = randomString()
    rs_version = '1.0'

    sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                           txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                           rs_version=rs_version, rs_type=rs_type, rs_content=content)

    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }
    get_rich_schema_by_metadata_operation.pop(absent_meta, None)

    with pytest.raises(RequestNackedException, match='missed fields'):
        sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                            sdk_wallet_endorser,
                                            get_rich_schema_by_metadata_operation)
