import asyncio
from datetime import datetime, timedelta

import dateutil
import pytest

from indy_node.server.restart_log import RestartLog
from plenum.common.exceptions import RequestRejectedException

from indy_common.constants import POOL_RESTART, ACTION, START, DATETIME, CANCEL
from indy_node.test.pool_restart.helper import _createServer, _stopServer
from plenum.common.constants import REPLY, TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply, sdk_get_and_check_replies
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching


def test_pool_restart(
        sdk_pool_handle, sdk_wallet_trustee, looper, tconf, txnPoolNodeSet):

    server, indicator = looper.loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )

    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    start_at = unow + timedelta(seconds=1000)
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
        DATETIME: str(datetime.isoformat(start_at))
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       req_obj)
    req_json, resp = sdk_get_reply(looper, req, 100)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.SCHEDULED
    _stopServer(server)
    _comparison_reply(resp, req_obj)


def test_pool_restart_cancel(
        sdk_pool_handle, sdk_wallet_trustee, looper, tconf, txnPoolNodeSet):
    loop = asyncio.get_event_loop()
    server, indicator = loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )

    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    start_at = unow + timedelta(seconds=100)
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
        DATETIME: str(start_at)
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       req_obj)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.SCHEDULED
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: CANCEL,
        DATETIME: str(datetime.isoformat(start_at))
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    req_json, resp = sdk_get_reply(looper, req, 100)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.CANCELLED
    _stopServer(server)
    _comparison_reply(resp, req_obj)
    assert resp[f.RESULT.nm][DATETIME] == str(datetime.isoformat(start_at))


def test_pool_restart_now(
        sdk_pool_handle, sdk_wallet_trustee, looper, tdir, tconf):
    server, indicator = looper.loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       req_obj)
    is_reply_received = False
    try:
        req_json, resp = sdk_get_reply(looper, req, 100)
    except Exception as ex:
        assert "Timeout" in ex.args
    _stopServer(server)
    if is_reply_received:
        _comparison_reply(resp, req_obj)


def test_fail_pool_restart(
        sdk_pool_handle, sdk_wallet_steward, looper):
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_steward[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_steward,
                                      req_obj)
    with pytest.raises(RequestRejectedException) as excinfo:
        sdk_get_and_check_replies(looper, [req], 100)
    assert excinfo.match("STEWARD cannot do restart")


def _comparison_reply(resp, req_obj):
    assert resp["op"] == REPLY
    assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj.identifier
    assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj.reqId
    assert resp[f.RESULT.nm][ACTION]
    assert resp[f.RESULT.nm][TXN_TYPE] == POOL_RESTART

