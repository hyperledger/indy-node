import copy

import time
from indy.ledger import build_get_revoc_reg_def_request, build_get_revoc_reg_request, build_get_revoc_reg_delta_request

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_node.test.anon_creds.helper import get_revoc_reg_def_id

from common.serializers.serialization import domain_state_serializer
from indy_node.test.auth_rule.helper import sdk_send_and_check_get_auth_rule_request, generate_key, \
    sdk_send_and_check_auth_rule_request
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, \
    ROLE, VERKEY, TXN_TIME, NYM, NAME, VERSION, STEWARD
from plenum.common.types import f

from indy_node.test.state_proof.helper import check_valid_proof, \
    sdk_submit_operation_and_get_result
from indy_common.constants import GET_ATTR, GET_NYM, SCHEMA, GET_SCHEMA, \
    CLAIM_DEF, REVOCATION, GET_CLAIM_DEF, CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_FROM, \
    SCHEMA_ATTR_NAMES, SCHEMA_NAME, SCHEMA_VERSION, CLAIM_DEF_TAG, ENDORSER
from indy_common.serialization import attrib_raw_data_serializer

# Fixtures, do not remove
from indy_node.test.attrib_txn.test_nym_attrib import \
    sdk_added_raw_attribute, attributeName, attributeValue, attributeData
from indy_node.test.schema.test_send_get_schema import send_schema_seq_no
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_req

from indy_node.test.anon_creds.conftest import send_revoc_reg_entry, send_revoc_reg_def, send_claim_def, claim_def
from indy_node.test.schema.test_send_get_schema import send_schema_req


def test_state_proof_returned_for_get_attr(looper,
                                           nodeSetWithOneNodeResponding,
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
        TARGET_NYM: sdk_added_raw_attribute['result']['txn']['data']['dest'],
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_attr_operation)
    expected_data = attrib_raw_data_serializer.deserialize(attributeData)
    assert DATA in result
    data = attrib_raw_data_serializer.deserialize(result[DATA])
    assert data == expected_data
    assert result[TXN_TIME]
    check_valid_proof(result)


def test_state_proof_returned_for_get_nym(looper,
                                          nodeSetWithOneNodeResponding,
                                          sdk_user_wallet_a,
                                          sdk_pool_handle,
                                          sdk_wallet_client,
                                          sdk_wallet_endorser):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_user_wallet_a

    nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: NYM
    }

    sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                        sdk_wallet_endorser,
                                        nym_operation)

    get_nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_NYM
    }

    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_nym_operation)
    assert DATA in result
    assert result[DATA]
    data = domain_state_serializer.deserialize(result[DATA])
    assert ROLE in data
    assert VERKEY in data
    assert f.IDENTIFIER.nm in data
    assert result[TXN_TIME]
    check_valid_proof(result)


def test_state_proof_returned_for_get_schema(looper,
                                             nodeSetWithOneNodeResponding,
                                             sdk_wallet_endorser,
                                             sdk_pool_handle,
                                             sdk_wallet_client):
    """
    Tests that state proof is returned in the reply for GET_SCHEMA transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_wallet_endorser
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
    sdk_submit_operation_and_get_result(looper,
                                        sdk_pool_handle,
                                        sdk_wallet_endorser,
                                        schema_operation)

    get_schema_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            NAME: schema_name,
            VERSION: schema_version,
        }
    }
    result = sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_schema_operation)
    assert DATA in result
    data = result.get(DATA)
    assert data
    assert SCHEMA_ATTR_NAMES in data
    assert data[SCHEMA_ATTR_NAMES] == schema_attr_names
    assert NAME in data
    assert VERSION in data
    assert result[TXN_TIME]
    check_valid_proof(result)


def test_state_proof_returned_for_get_claim_def(looper,
                                                nodeSetWithOneNodeResponding,
                                                sdk_wallet_endorser,
                                                sdk_pool_handle,
                                                sdk_wallet_client,
                                                send_schema_seq_no):
    """
    Tests that state proof is returned in the reply for GET_CLAIM_DEF
    transactions.
    Use different submitter and reader!
    """
    _, dest = sdk_wallet_endorser
    data = {"primary": {'N': '123'}, REVOCATION: {'h0': '456'}}
    claim_def_operation = {
        TXN_TYPE: CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: send_schema_seq_no,
        DATA: data,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL',
        CLAIM_DEF_TAG: "tag1"
    }
    sdk_submit_operation_and_get_result(looper,
                                        sdk_pool_handle,
                                        sdk_wallet_endorser,
                                        claim_def_operation)
    get_claim_def_operation = {
        CLAIM_DEF_FROM: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        CLAIM_DEF_SCHEMA_REF: send_schema_seq_no,
        CLAIM_DEF_SIGNATURE_TYPE: 'CL',
        CLAIM_DEF_TAG: "tag1"
    }
    result = sdk_submit_operation_and_get_result(looper,
                                                 sdk_pool_handle,
                                                 sdk_wallet_client,
                                                 get_claim_def_operation)
    expected_data = data
    assert DATA in result
    data = result.get(DATA)
    assert data
    assert data == expected_data
    assert result[TXN_TIME]
    check_valid_proof(result)


def test_state_proof_returned_for_get_auth_rule(looper,
                                                nodeSetWithOneNodeResponding,
                                                sdk_wallet_steward,
                                                sdk_pool_handle,
                                                sdk_wallet_client,
                                                send_auth_rule):
    req = send_auth_rule

    key = generate_key(auth_action=ADD_PREFIX, auth_type=NYM,
                       field=ROLE, new_value=ENDORSER)
    rep = sdk_send_and_check_get_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_client, **key)
    result = rep[0][1]['result']

    expected_data = req[0][0]['operation']
    del expected_data['type']
    assert DATA in result
    data = result.get(DATA)
    assert data
    assert data[0] == expected_data
    check_valid_proof(result)


def test_state_proof_returned_for_get_revoc_reg_def(looper,
                                                    nodeSetWithOneNodeResponding,
                                                    sdk_wallet_steward,
                                                    sdk_pool_handle,
                                                    sdk_wallet_client,
                                                    send_revoc_reg_def):
    revoc_reg_def_data = send_revoc_reg_def[0]['operation']

    req = looper.loop.run_until_complete(build_get_revoc_reg_def_request(
        sdk_wallet_client[1], get_revoc_reg_def_id(sdk_wallet_steward[1], send_revoc_reg_def[0])))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, req)])
    result = rep[0][1]['result']

    expected_data = revoc_reg_def_data
    del expected_data['type']
    assert DATA in result
    data = result.get(DATA)
    assert data
    assert data == expected_data
    assert result[TXN_TIME]
    check_valid_proof(result)


def test_state_proof_returned_for_get_revoc_reg_entry(looper,
                                                      nodeSetWithOneNodeResponding,
                                                      sdk_wallet_steward,
                                                      sdk_pool_handle,
                                                      sdk_wallet_client,
                                                      send_revoc_reg_entry):
    revoc_reg_def = send_revoc_reg_entry[0]
    revoc_reg_entry_data = send_revoc_reg_entry[1][0]['operation']

    timestamp = int(time.time())
    req = looper.loop.run_until_complete(build_get_revoc_reg_request(
        sdk_wallet_client[1], get_revoc_reg_def_id(sdk_wallet_steward[1], revoc_reg_def[0]), timestamp))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, req)])
    result = rep[0][1]['result']

    expected_data = revoc_reg_entry_data
    data = result.get(DATA)

    del expected_data['type']
    del data['seqNo']
    del data['txnTime']
    assert DATA in result
    assert data
    assert data == expected_data
    assert result[TXN_TIME]
    check_valid_proof(result)


def check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp_fr, timestamp_to,
                    sdk_pool_handle, revoc_reg_entry_data, check_data=True):
    req = looper.loop.run_until_complete(build_get_revoc_reg_delta_request(
        sdk_wallet_client[1], get_revoc_reg_def_id(sdk_wallet_steward[1], revoc_reg_def[0]), timestamp_fr,
        timestamp_to))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, req)])

    if check_data:
        result = rep[0][1]['result']
        expected_data = revoc_reg_entry_data
        data = result.get(DATA)['value']['accum_to']

        del data['seqNo']
        del data['txnTime']
        if 'type' in expected_data:
            del expected_data['type']
        assert DATA in result
        assert data
        assert data == expected_data
        assert result[TXN_TIME]
        check_valid_proof(result)


def test_state_proof_returned_for_get_revoc_reg_delta(looper,
                                                      nodeSetWithOneNodeResponding,
                                                      sdk_wallet_steward,
                                                      sdk_pool_handle,
                                                      sdk_wallet_client,
                                                      send_revoc_reg_entry):
    revoc_reg_def = send_revoc_reg_entry[0]
    revoc_reg_entry_data = send_revoc_reg_entry[1][0]['operation']
    timestamp = send_revoc_reg_entry[1][1]['result']['txnMetadata']['txnTime']

    check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, None, timestamp + 1,
                    sdk_pool_handle, revoc_reg_entry_data)

    check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, None, timestamp - 1,
                    sdk_pool_handle, revoc_reg_entry_data, False)

    # TODO: INDY-2115
    # check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp - 2, timestamp - 1,
    #                 sdk_pool_handle, revoc_reg_entry_data, False)

    # TODO: INDY-2158
    # check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp - 1, timestamp + 1,
    #                 sdk_pool_handle, revoc_reg_entry_data)

    check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp + 1, timestamp + 2,
                    sdk_pool_handle, revoc_reg_entry_data)

    # TODO: INDY-2115
    # check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, None, timestamp - 999,
    #                 sdk_pool_handle, revoc_reg_entry_data)
    #
    # check_get_delta(looper, sdk_wallet_client, sdk_wallet_steward, revoc_reg_def, timestamp - 1000, timestamp - 999,
    #                 sdk_pool_handle, revoc_reg_entry_data)
