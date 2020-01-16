import asyncio
from datetime import datetime, timedelta

import dateutil
from jsonpickle import json

from indy_node.server.restart_log import RestartLog, RestartLogData

from indy_common.constants import POOL_RESTART, ACTION, START, CANCEL
from indy_node.server.restarter import Restarter
from indy_node.test.pool_restart.helper import _createServer, _stopServer, sdk_send_restart
from plenum.common.constants import REPLY, TXN_TYPE
from plenum.common.types import f
from plenum.test.testing_utils import FakeSomething


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
        assert node.restarter.lastActionEventInfo.ev_type == RestartLog.Events.scheduled
    _comparison_reply(responses, req_obj)


def test_restarter_can_initialize_after_pool_restart(txnPoolNodeSet):
    '''
    1. Add restart schedule message to ActionLog
    2. Add start restart message to ActionLog
    3. Check that Restarter can be create (emulate case after node restart).
    '''
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    restarted_node = txnPoolNodeSet[-1]
    ev_data = RestartLogData(unow)
    restarted_node.restarter._actionLog.append_scheduled(ev_data)
    restarted_node.restarter._actionLog.append_started(ev_data)
    Restarter(restarted_node.id,
              restarted_node.name,
              restarted_node.dataLocation,
              restarted_node.config,
              actionLog=restarted_node.restarter._actionLog)


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
        assert node.restarter.lastActionEventInfo.ev_type == RestartLog.Events.scheduled
    _comparison_reply(responses, req_obj)

    req_obj, responses = sdk_send_restart(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          action=CANCEL,
                                          datetime="")
    _stopServer(server)
    for node in txnPoolNodeSet:
        assert node.restarter.lastActionEventInfo.ev_type == RestartLog.Events.cancelled
    _comparison_reply(responses, req_obj)


def test_pool_restart_now_without_datetime(
        sdk_pool_handle, sdk_wallet_trustee, looper, tdir, tconf):
    pool_restart_now(sdk_pool_handle, sdk_wallet_trustee, looper,
                     tdir, tconf, START)


def test_pool_restart_in_view_change(sdk_pool_handle, sdk_wallet_trustee, looper,
                                     tdir, tconf, txnPoolNodeSet):

    for node in txnPoolNodeSet:
        node.master_replica._consensus_data.waiting_for_new_view = True

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

    req_obj, resp = sdk_send_restart(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     action=action,
                                     datetime=datetime)
    _stopServer(server)
    _comparison_reply(resp, req_obj)


def _check_restart_log(item, action, when=None):
    assert item.ev_type == action and (
            when is None or str(datetime.isoformat(item.data.when)) == when)


def _comparison_reply(responses, req_obj):
    for json_resp in responses.values():
        resp = json.loads(json_resp)
        assert resp["op"] == REPLY
        assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj[f.IDENTIFIER.nm]
        assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj[f.REQ_ID.nm]
        assert resp[f.RESULT.nm][ACTION]
        assert resp[f.RESULT.nm][TXN_TYPE] == POOL_RESTART
