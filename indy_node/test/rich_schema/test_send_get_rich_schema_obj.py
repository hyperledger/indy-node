import json

import pytest

from indy_common.constants import JSON_LD_CONTEXT, RICH_SCHEMA, RICH_SCHEMA_ENCODING, \
    RICH_SCHEMA_MAPPING, RICH_SCHEMA_CRED_DEF, \
    RS_CONTEXT_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, \
    GET_RICH_SCHEMA_OBJECT_BY_ID, RS_ID, GET_RICH_SCHEMA_OBJECT_BY_METADATA, RS_NAME, RS_VERSION, RS_TYPE, \
    RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE
from indy_node.test.api.helper import sdk_write_rich_schema_object_and_check
from indy_node.test.helper import rich_schemas_enabled_scope
from indy_node.test.rich_schema.templates import RICH_SCHEMA_EX1, W3C_BASE_CONTEXT, RICH_SCHEMA_PRES_DEF_EX1, \
    RICH_SCHEMA_CRED_DEF_EX1, RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_ENCODING_EX1
from indy_node.test.state_proof.helper import check_valid_proof, sdk_submit_operation_and_get_result
from plenum.common.constants import TXN_TYPE
from plenum.common.exceptions import RequestNackedException
from plenum.common.util import randomString, SortedDict


@pytest.fixture(scope="module")
def tconf(tconf):
    with rich_schemas_enabled_scope(tconf):
        yield tconf

# The order of creation is essential as some rich schema object reference others by ID
# Encoding's id must be equal to the one used in RICH_SCHEMA_MAPPING_EX1

# txn_type, rs_type, content, rs_id, rs_name, rs_version:
PARAMS = [
    (
        JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, W3C_BASE_CONTEXT, randomString(), randomString(), '1.0'
    ),
    (
        RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, RICH_SCHEMA_EX1, RICH_SCHEMA_EX1['@id'], randomString(), '2.0'
    ),
    (
        RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA_ENCODING_EX1,
        "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD", randomString(), '1.1'
    ),
    (
        RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_MAPPING_EX1['@id'],
        randomString(),
        '10.0'
    ),
    (
        RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA_CRED_DEF_EX1, randomString(),
        randomString(), '1000.0'
    ),
    (
        RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE, RICH_SCHEMA_PRES_DEF_EX1, RICH_SCHEMA_PRES_DEF_EX1['@id'],
        randomString(), '1.1000.1'
    )
]


@pytest.fixture(scope='module')
def write_rich_schema(looper, sdk_pool_handle, sdk_wallet_endorser):
    for txn_type, rs_type, content, rs_id, rs_name, rs_version in PARAMS:
        sdk_write_rich_schema_object_and_check(looper, sdk_wallet_endorser, sdk_pool_handle,
                                               txn_type=txn_type, rs_id=rs_id, rs_name=rs_name,
                                               rs_version=rs_version, rs_type=rs_type, rs_content=content)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                        write_rich_schema,
                                        txn_type, rs_type, content, rs_id, rs_name, rs_version):
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
        'content': json.dumps(content),
        'from': sdk_wallet_endorser[1],
        'endorser': None,
        'ver': None
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo']
    assert result['txnTime']
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_metadata(looper, sdk_pool_handle, sdk_wallet_endorser, sdk_wallet_client,
                                              write_rich_schema,
                                              txn_type, rs_type, content, rs_id, rs_name, rs_version):
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
        'content': json.dumps(content),
        'from': sdk_wallet_endorser[1],
        'endorser': None,
        'ver': None
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo']
    assert result['txnTime']
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_invalid_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                write_rich_schema,
                                                txn_type, rs_type, content, rs_id, rs_name, rs_version):
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


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
@pytest.mark.parametrize('invalid_meta_name, invalid_meta_value', [(RS_NAME, randomString()),
                                                                   (RS_VERSION, "100.3"),
                                                                   (RS_TYPE, randomString())])
def test_send_get_rich_schema_obj_by_invalid_metadata(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                      write_rich_schema,
                                                      txn_type, rs_type, content, rs_id, rs_name, rs_version,
                                                      invalid_meta_name, invalid_meta_value):
    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }
    get_rich_schema_by_metadata_operation[invalid_meta_name] = invalid_meta_value

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_rich_schema_by_metadata_operation)
    assert result['data'] is None
    assert result['seqNo'] is None
    assert result['txnTime'] is None
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
def test_send_get_rich_schema_obj_by_no_id(looper, sdk_pool_handle, sdk_wallet_endorser,
                                           write_rich_schema,
                                           txn_type, rs_type, content, rs_id, rs_name, rs_version):
    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
    }

    with pytest.raises(RequestNackedException, match='missed fields'):
        sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                            sdk_wallet_endorser,
                                            get_rich_schema_by_id_operation)


@pytest.mark.parametrize('txn_type, rs_type, content, rs_id, rs_name, rs_version', PARAMS)
@pytest.mark.parametrize('absent_meta', [RS_NAME, RS_VERSION, RS_TYPE])
def test_send_get_rich_schema_obj_by_no_metadata(looper, sdk_pool_handle, sdk_wallet_endorser,
                                                 write_rich_schema,
                                                 txn_type, rs_type, content, rs_id, rs_name, rs_version,
                                                 absent_meta):
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
