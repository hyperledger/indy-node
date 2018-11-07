from common.serializers.serialization import domain_state_serializer
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, \
    ROLE, VERKEY, TXN_TIME, NYM, NAME, VERSION, ORIGIN
from plenum.common.types import f

from indy_client.test.state_proof.helper import check_valid_proof, \
    sdk_submit_operation_and_get_replies
from indy_common.constants import GET_ATTR, GET_NYM, SCHEMA, GET_SCHEMA, \
    CLAIM_DEF, REVOCATION, GET_CLAIM_DEF, CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_FROM, \
    SCHEMA_ATTR_NAMES, SCHEMA_NAME, SCHEMA_VERSION
from indy_common.serialization import attrib_raw_data_serializer

# Fixtures, do not remove
from indy_client.test.test_nym_attrib import \
    sdk_added_raw_attribute, attributeName, attributeValue, attributeData


def test_state_proof_returned_for_get_attr(looper,
                                           sdk_added_raw_attribute,
                                           attributeName,
                                           attributeData,
                                           sdk_pool_handle,
                                           sdk_wallet_client):
    """
    Tests that state proof is returned in the reply for GET_ATTR transactions.
    Use different submitter and reader!
    """
    get_attr_operation = {
        TARGET_NYM: sdk_added_raw_attribute['operation']['dest'],
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_client,
                                                   get_attr_operation)
    expected_data = attrib_raw_data_serializer.deserialize(attributeData)
    for reply in replies:
        result = reply[1]['result']
        assert DATA in result
        data = attrib_raw_data_serializer.deserialize(result[DATA])
        assert data == expected_data
        assert result[TXN_TIME]
        check_valid_proof(reply[1])


def test_state_proof_returned_for_get_nym(looper,
                                          sdk_user_wallet_a,
                                          sdk_pool_handle,
                                          sdk_wallet_client,
                                          sdk_wallet_trust_anchor):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_user_wallet_a

    nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: NYM
    }

    sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                         sdk_wallet_trust_anchor,
                                         nym_operation)

    get_nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_NYM
    }

    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_client,
                                                   get_nym_operation)
    for reply in replies:
        result = reply[1]['result']
        assert DATA in result
        assert result[DATA]
        data = domain_state_serializer.deserialize(result[DATA])
        assert ROLE in data
        assert VERKEY in data
        assert f.IDENTIFIER.nm in data
        assert result[TXN_TIME]
        check_valid_proof(reply[1])


def test_state_proof_returned_for_get_schema(looper,
                                             sdk_wallet_trust_anchor,
                                             sdk_pool_handle,
                                             sdk_wallet_client):
    """
    Tests that state proof is returned in the reply for GET_SCHEMA transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_wallet_trust_anchor
    schema_name = "test_schema"
    schema_version = "1.0"
    schema_attr_names = ["width", "height"]
    data = {
        SCHEMA_NAME: schema_name,
        SCHEMA_VERSION: schema_version,
        SCHEMA_ATTR_NAMES: schema_attr_names
    }
    schema_operation = {
        TXN_TYPE: SCHEMA,
        DATA: data
    }
    sdk_submit_operation_and_get_replies(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trust_anchor,
                                         schema_operation)

    get_schema_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            NAME: schema_name,
            VERSION: schema_version,
        }
    }
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_client,
                                                   get_schema_operation)
    for reply in replies:
        result = reply[1]['result']
        assert DATA in result
        data = result.get(DATA)
        assert data
        assert SCHEMA_ATTR_NAMES in data
        assert data[SCHEMA_ATTR_NAMES] == schema_attr_names
        assert NAME in data
        assert VERSION in data
        assert result[TXN_TIME]
        check_valid_proof(reply[1])


def test_state_proof_returned_for_get_claim_def(looper,
                                                sdk_wallet_trust_anchor,
                                                sdk_pool_handle,
                                                sdk_wallet_client):
    """
    Tests that state proof is returned in the reply for GET_CLAIM_DEF
    transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_wallet_trust_anchor
    data = {"primary": {'N': '123'}, REVOCATION: {'h0': '456'}}
    claim_def_operation = {
        TXN_TYPE: CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: 12,
        DATA: data,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL'
    }
    sdk_submit_operation_and_get_replies(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trust_anchor,
                                         claim_def_operation)
    get_claim_def_operation = {
        CLAIM_DEF_FROM: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: 12,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL'
    }
    replies = sdk_submit_operation_and_get_replies(looper,
                                                   sdk_pool_handle,
                                                   sdk_wallet_client,
                                                   get_claim_def_operation)
    expected_data = data
    for reply in replies:
        result = reply[1]['result']
        assert DATA in result
        data = result.get(DATA)
        assert data
        assert data == expected_data
        assert result[TXN_TIME]
        check_valid_proof(reply[1])
