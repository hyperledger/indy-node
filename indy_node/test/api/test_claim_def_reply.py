import json

from indy.anoncreds import issuer_create_and_store_credential_def
from indy.ledger import build_cred_def_request, sign_request, submit_request

from indy_node.test.api.helper import validate_write_reply, validate_claim_def_txn, sdk_write_schema


def test_claim_def_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward

    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_steward, "id", ["first", "last"])
    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))

    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    reply = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    validate_write_reply(reply)
    validate_claim_def_txn(reply['result']['txn'])
