import pytest

from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA

from indy_node.test.state_proof.helper import check_valid_proof, \
    sdk_submit_operation_and_get_result
from indy_common.constants import GET_ATTR, GET_NYM, GET_SCHEMA, GET_CLAIM_DEF, CLAIM_DEF_FROM, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES

# fixtures, do not remove
from indy_node.test.attrib_txn.test_nym_attrib import \
    sdk_added_raw_attribute, attributeName, attributeValue, attributeData


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
