import json

from indy.anoncreds import issuer_create_and_store_credential_def
from indy.ledger import build_cred_def_request, build_get_schema_request, parse_get_schema_response
from indy_node.test.api.helper import validate_write_reply, validate_claim_def_txn, sdk_write_schema
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req


def test_claim_def_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward

    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_steward)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))

    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]

    validate_write_reply(reply)
    validate_claim_def_txn(reply['result']['txn'])
