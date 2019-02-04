from indy.ledger import build_nym_request
from indy_node.test.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy_node.test.api.helper import validate_write_reply, validate_nym_txn
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req


def test_nym_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    _, identifier = sdk_wallet_steward
    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]

    validate_write_reply(reply)
    validate_nym_txn(reply['result']['txn'])
