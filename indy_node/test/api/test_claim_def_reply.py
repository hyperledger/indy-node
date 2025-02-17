import json

from indy.ledger import parse_get_schema_response
from indy_node.test.utils import create_and_store_cred_def
from indy_vdr import ledger
from indy_node.test.api.helper import validate_write_reply, validate_claim_def_txn, sdk_write_schema
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req

# need to look a how the reply is formatted to replace the parsing method
# build_cred_def_request and build_get_schema_requests already returns a request might not need to use the looper to create one
# Needs to be tested once plenum is updated to use indy-vdr
def test_claim_def_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward

    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_steward)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(ledger.build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))

    _, definition_json = looper.loop.run_until_complete(create_and_store_cred_def(
        wallet_handle, identifier, schema_json, "some_tag", "CL", True))
    request = looper.loop.run_until_complete(ledger.build_cred_def_request(identifier, definition_json))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]

    validate_write_reply(reply)
    validate_claim_def_txn(reply['result']['txn'])
