import asyncio
from datetime import datetime, timedelta

import dateutil
from jsonpickle import json

from indy_node.server.restart_log import RestartLog

from indy_common.constants import POOL_RESTART, ACTION, START, CANCEL
from indy_node.test.pool_restart.helper import _createServer, _stopServer, sdk_send_restart
from plenum.common.constants import REPLY, TXN_TYPE
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
    req_obj, responses = sdk_send_restart(looper,
                           sdk_wallet_trustee,
                           sdk_pool_handle,
                           action=START,
                           datetime=str(datetime.isoformat(start_at)))

    _stopServer(server)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.SCHEDULED
    _comparison_reply(responses, req_obj)


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
    start_at = unow + timedelta(seconds=1000)
    req_obj, responses = sdk_send_restart(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          action=START,
                                          datetime=str(datetime.isoformat(start_at)))
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.SCHEDULED
    _comparison_reply(responses, req_obj)

    req_obj, responses = sdk_send_restart(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     action=CANCEL,
                                     datetime="")
    _stopServer(server)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo[0] == RestartLog.CANCELLED
    _comparison_reply(responses, req_obj)


def test_pool_restart_now_without_datetime(
        sdk_pool_handle, sdk_wallet_trustee, looper, tdir, tconf):
    pool_restart_now(sdk_pool_handle, sdk_wallet_trustee, looper,
                     tdir, tconf, START)


def pool_restart_now(sdk_pool_handle, sdk_wallet_trustee, looper, tdir, tconf,
                     action, datetime=None):
    server, indicator = looper.loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )
    _stopServer(server)

    req_obj, resp = sdk_send_restart(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     action=action,
                                     datetime=datetime)
    _comparison_reply(resp, req_obj)


def _check_restart_log(item, action, when=None):
    assert item[1] == action and (
            when is None or str(datetime.isoformat(item[2])) == when)


def _comparison_reply(responses, req_obj):
    for json_resp in responses.values():
        resp = json.loads(json_resp)
        assert resp["op"] == REPLY
        assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj[f.IDENTIFIER.nm]
        assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj[f.REQ_ID.nm]
        assert resp[f.RESULT.nm][ACTION]
        assert resp[f.RESULT.nm][TXN_TYPE] == POOL_RESTART
