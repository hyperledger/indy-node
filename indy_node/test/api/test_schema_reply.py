import json

from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request, sign_request, submit_request
from indy_node.test.api.helper import validate_write_reply, validate_schema_txn


def test_schema_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward

    _, schema_json = looper.loop.run_until_complete(issuer_create_schema(identifier, "id", "1.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    reply = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    validate_write_reply(reply)
    validate_schema_txn(reply['result']['txn'])
