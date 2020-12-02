import pytest

from indy_common.constants import GET_ATTR, GET_NYM, GET_SCHEMA, GET_CLAIM_DEF, CLAIM_DEF_FROM, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES, JSON_LD_CONTEXT, RICH_SCHEMA, \
    RICH_SCHEMA_ENCODING, RICH_SCHEMA_MAPPING, RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE, \
    RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE, RS_CONTEXT_TYPE_VALUE, RS_ID, \
    GET_RICH_SCHEMA_OBJECT_BY_ID, GET_RICH_SCHEMA_OBJECT_BY_METADATA, RS_NAME, RS_VERSION, RS_TYPE, \
    RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE
from indy_node.test.rich_schema.templates import W3C_BASE_CONTEXT, RICH_SCHEMA_EX1
from indy_node.test.state_proof.helper import check_valid_proof, \
    sdk_submit_operation_and_get_result
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA
# fixtures, do not remove
from indy_node.test.attrib_txn.test_nym_attrib import \
    sdk_added_raw_attribute, attributeName, attributeValue, attributeData

from plenum.common.util import randomString


def check_no_data_and_valid_proof(result):
    assert result.get(DATA) is None
    check_valid_proof(result)


def test_state_proof_returned_for_missing_attr(looper, nodeSetWithOneNodeResponding,
                                               attributeName,
                                               sdk_pool_handle,
                                               sdk_wallet_endorser):
    """
    Tests that state proof is returned in the reply for GET_ATTR transactions
    """
    _, dest = sdk_wallet_endorser

    get_attr_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser, get_attr_operation)
    check_no_data_and_valid_proof(result)


def test_state_proof_returned_for_missing_nym(looper, nodeSetWithOneNodeResponding,
                                              sdk_pool_handle,
                                              sdk_wallet_endorser,
                                              sdk_user_wallet_a):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions
    """
    # Make not existing id
    _, dest = sdk_user_wallet_a
    dest = dest[:-3]
    dest += "fff"

    get_nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_NYM
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser, get_nym_operation)
    check_no_data_and_valid_proof(result)


def test_state_proof_returned_for_missing_schema(looper, nodeSetWithOneNodeResponding,
                                                 sdk_pool_handle,
                                                 sdk_wallet_endorser):
    """
    Tests that state proof is returned in the reply for GET_SCHEMA transactions
    """
    _, dest = sdk_wallet_endorser
    schema_name = "test_schema"
    schema_version = "1.0"
    get_schema_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            SCHEMA_NAME: schema_name,
            SCHEMA_VERSION: schema_version,
        }
    }
    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_schema_operation)
    assert SCHEMA_ATTR_NAMES not in result[DATA]
    check_valid_proof(result)


def test_state_proof_returned_for_missing_claim_def(looper, nodeSetWithOneNodeResponding,
                                                    sdk_pool_handle,
                                                    sdk_wallet_endorser):
    """
    Tests that state proof is returned in the reply for GET_CLAIM_DEF
    transactions
    """
    _, dest = sdk_wallet_endorser
    get_claim_def_operation = {
        CLAIM_DEF_FROM: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: 12,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL'
    }
    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_endorser,
                                                 get_claim_def_operation)
    check_no_data_and_valid_proof(result)


@pytest.mark.skip
# TODO fix this test so it does not rely on Indy-SDK,
# or, fix this test once Rich Schema objects are part of Indy-SDK
def test_state_proof_returned_for_missing_get_rich_schema_obj_by_id(looper,
                                                                    nodeSetWithOneNodeResponding,
                                                                    sdk_wallet_endorser,
                                                                    sdk_pool_handle,
                                                                    sdk_wallet_client):
    """
    Tests that state proof is returned in the reply for GET_RICH_SCHEMA_OBJECT_BY_ID.
    Use different submitter and reader!
    """
    rs_id = randomString()
    get_rich_schema_by_id_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
        RS_ID: rs_id,
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_rich_schema_by_id_operation)
    check_no_data_and_valid_proof(result)


@pytest.mark.skip
# TODO fix this test so it does not rely on Indy-SDK,
# or, fix this test once Rich Schewma objects are part of Indy-SDK
@pytest.mark.parametrize('rs_type',
                         [RS_CONTEXT_TYPE_VALUE, RS_SCHEMA_TYPE_VALUE, RS_ENCODING_TYPE_VALUE, RS_MAPPING_TYPE_VALUE,
                          RS_CRED_DEF_TYPE_VALUE, RS_PRES_DEF_TYPE_VALUE])
def test_state_proof_returned_for_missing_get_rich_schema_obj_by_metadata(looper,
                                                                          nodeSetWithOneNodeResponding,
                                                                          sdk_wallet_endorser,
                                                                          sdk_pool_handle,
                                                                          sdk_wallet_client,
                                                                          rs_type):
    """
    Tests that state proof is returned in the reply for GET_RICH_SCHEMA_OBJECT_BY_ID.
    Use different submitter and reader!
    """
    rs_name = randomString()
    rs_version = '1.0'
    get_rich_schema_by_metadata_operation = {
        TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
        RS_NAME: rs_name,
        RS_VERSION: rs_version,
        RS_TYPE: rs_type
    }
    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_rich_schema_by_metadata_operation)
    check_no_data_and_valid_proof(result)
