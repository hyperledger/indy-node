import json

import time

from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy.ledger import sign_request, submit_request, build_nym_request
from indy.error import IndyError, ErrorCode
from plenum.common.constants import REPLY, REJECT, TXN_TYPE, DATA
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj


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


def test_pool_restart(
        sdk_pool_handle, sdk_wallet_steward, looper):
    schedule = time.time() + 1000*60
    # op = {
    #     TXN_TYPE: POOL_RESTART,
    #     DATA: {ACTION: START,
    #            SCHEDULE: schedule}
    # }
    op = {
        TXN_TYPE: "116",
        DATA: {"action": "start",
               "schedule": schedule}
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_steward[1])
    resp = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet_steward, req_obj)
    print(resp)
