import json

import pytest
from indy.anoncreds import issuer_create_and_store_credential_def, issuer_create_schema
from indy.ledger import build_cred_def_request, parse_get_schema_response, \
    build_get_schema_request, build_schema_request

from indy_common.constants import REF
from indy_node.test.api.helper import sdk_write_schema
from indy_node.test.helper import modify_field
from plenum.common.exceptions import RequestRejectedException
from plenum.common.types import OPERATION
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies, sdk_get_reply, max_3pc_batch_limits


def sdk_send_claim_def(looper, sdk_pool_handle, sdk_wallet, tag, schema_json):
    wallet_handle, identifier = sdk_wallet

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, tag, "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    reply = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet, request)])
    return reply


@pytest.fixture(scope="module")
def schema_json(looper, sdk_pool_handle, sdk_wallet_trustee):
    wallet_handle, identifier = sdk_wallet_trustee
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))
    return schema_json


def test_send_claim_def_succeeds(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    reply = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])


def test_send_claim_def_schema_and_claim_def_in_one_batch(
        looper, tconf, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    with max_3pc_batch_limits(tconf, size=2) as tconf:
        initial_seq_no = nodeSet[0].domainLedger.size
        wallet_handle, identifier = sdk_wallet_trustee

        # send SCHEMA
        _, schema_json = looper.loop.run_until_complete(
            issuer_create_schema(identifier, "name2", "2.0", json.dumps(["first", "last"])))
        schema_req_json = looper.loop.run_until_complete(
            build_schema_request(identifier, schema_json))
        schema_req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, schema_req_json)

        # send CLAIM_DEF
        _, claim_def_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
            wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))
        claim_def_req_json = looper.loop.run_until_complete(
            build_cred_def_request(identifier, claim_def_json))
        claim_def_req_json = modify_field(claim_def_req_json, initial_seq_no + 1, OPERATION, REF)
        claim_def_req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, claim_def_req_json)

        # check both are written
        sdk_get_and_check_replies(looper, [schema_req, claim_def_req])


def test_send_claim_def_fails_if_ref_is_seqno_of_non_schema_txn(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag1", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    request = modify_field(request, 1, OPERATION, REF)
    with pytest.raises(RequestRejectedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('isn\'t seqNo of the schema.')


def test_send_claim_def_fails_if_ref_is_not_existing_seqno(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag2", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    request = modify_field(request, 999999, OPERATION, REF)
    with pytest.raises(RequestRejectedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('doesn\'t exist')


def test_update_claim_def_for_same_schema_and_signature_type(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag3", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])

    definition_json = modify_field(definition_json, '999', 'value', 'primary', 'n')
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])


def test_can_send_same_claim_def_by_different_issuers(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, sdk_wallet_steward, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag4", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])

    wallet_handle, identifier = sdk_wallet_steward
    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag4", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request)])
