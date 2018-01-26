import json

from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy.ledger import sign_request, submit_request, build_nym_request


def test_nym_resend(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))

    result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))
    assert result['result']

    result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))
    assert result['result']