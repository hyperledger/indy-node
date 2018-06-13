from plenum.common.types import f
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, NAME, \
    VERSION, ORIGIN

from indy_client.test.state_proof.helper import check_valid_proof, \
    sdk_submit_operation_and_get_replies
from indy_common.constants import GET_ATTR, GET_NYM, GET_SCHEMA, GET_CLAIM_DEF, CLAIM_DEF_FROM, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES

# fixtures, do not remove
from indy_client.test.test_nym_attrib import \
    sdk_added_raw_attribute, attributeName, attributeValue, attributeData


def check_no_data_and_valid_proof(replies):
    for reply in replies:
        result = reply[1][f.RESULT.nm]
        assert result.get(DATA) is None
        check_valid_proof(reply[1])


def test_state_proof_returned_for_missing_attr(looper,
                                               attributeName,
                                               sdk_pool_handle,
                                               sdk_wallet_trust_anchor):
    """
    Tests that state proof is returned in the reply for GET_ATTR transactions
    """
    _, dest = sdk_wallet_trust_anchor

    get_attr_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_trust_anchor, get_attr_operation)
    check_no_data_and_valid_proof(replies)


def test_state_proof_returned_for_missing_nym(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_trust_anchor,
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

    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_trust_anchor, get_nym_operation)
    check_no_data_and_valid_proof(replies)


def test_state_proof_returned_for_missing_schema(looper,
                                                 sdk_pool_handle,
                                                 sdk_wallet_trust_anchor):
    """
    Tests that state proof is returned in the reply for GET_SCHEMA transactions
    """
    _, dest = sdk_wallet_trust_anchor
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
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_trust_anchor,
                                                   get_schema_operation)
    for reply in replies:
        result = reply[1][f.RESULT.nm]
        assert SCHEMA_ATTR_NAMES not in result[DATA]
        check_valid_proof(reply[1])


def test_state_proof_returned_for_missing_claim_def(looper,
                                                    sdk_pool_handle,
                                                    sdk_wallet_trust_anchor):
    """
    Tests that state proof is returned in the reply for GET_CLAIM_DEF
    transactions
    """
    _, dest = sdk_wallet_trust_anchor
    get_claim_def_operation = {
        CLAIM_DEF_FROM: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: 12,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL'
    }
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_trust_anchor,
                                                   get_claim_def_operation)
    check_no_data_and_valid_proof(replies)
