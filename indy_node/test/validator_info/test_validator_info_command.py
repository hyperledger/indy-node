import asyncio
from datetime import datetime, timedelta

import dateutil
import pytest
from plenum.common.exceptions import RequestRejectedException

from indy_common.constants import POOL_RESTART, ACTION, START, DATETIME, CANCEL, \
    VALIDATOR_INFO
from indy_node.test.pool_restart.helper import _createServer, _stopServer
from plenum.common.constants import REPLY, TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply, sdk_send_signed_requests, sdk_get_and_check_replies


def test_validator_info_command(
        sdk_pool_handle, sdk_wallet_trustee, looper):
    op = {
        TXN_TYPE: VALIDATOR_INFO
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    #req_json, resp = sdk_get_reply(looper, req, 100)
    # _comparison_reply(resp, req_obj)


def test_fail_validator_info_command(
        sdk_pool_handle, sdk_wallet_client, looper):
    op = {
        TXN_TYPE: VALIDATOR_INFO
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_client[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_client,
                                      req_obj)
    with pytest.raises(RequestRejectedException) as excinfo:
        sdk_get_and_check_replies(looper, [req], 100)
    assert excinfo.match("None role cannot do action with type = " +
                         VALIDATOR_INFO)


def _comparison_reply(resp, req_obj):
    assert resp["op"] == REPLY
    assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj.identifier
    assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj.reqId
    assert resp[f.RESULT.nm][TXN_TYPE] == VALIDATOR_INFO
    assert resp[f.RESULT.nm][DATA] is not None


