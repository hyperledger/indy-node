import json

from indy.ledger import build_nym_request, sign_request, submit_request
from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy_node.test.api.helper import validate_write_reply, validate_nym_txn


def test_nym_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    reply = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    validate_write_reply(reply)
    validate_nym_txn(reply['result']['txn'])
