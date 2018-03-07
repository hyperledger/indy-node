import json

from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy.ledger import sign_request, submit_request, build_nym_request
from indy.error import IndyError, ErrorCode
from plenum.common.constants import REPLY, REJECT


def test_nym_send_twice(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    for i in range(2):
        request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
        req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
        result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

        if i == 0:
            assert result['op'] == REPLY
        else:
            assert result['op'] == REJECT


def test_nym_resend(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))

    for i in range(2):
        result = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))
        assert result['op'] == REPLY
