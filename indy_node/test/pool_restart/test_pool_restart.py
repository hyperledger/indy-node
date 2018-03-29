import asyncio
from datetime import datetime, timedelta

import dateutil

from indy_common.constants import POOL_RESTART, ACTION, START, SCHEDULE, CANCEL
from indy_node.test.pool_restart.helper import _createServer, _stopServer
from plenum.common.constants import REPLY, TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching


def test_pool_restart(
        sdk_pool_handle, sdk_wallet_trustee, looper, tconf):

    #loop = asyncio.get_event_loop()
    server, indicator = looper.loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )
    #indicator.add_done_callback(_stopServer(server))

    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    start_at = unow + timedelta(seconds=1000)
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
        SCHEDULE: str(datetime.isoformat(start_at))
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       req_obj)
    req_json, resp = sdk_get_reply(looper, req, 100)
    _stopServer(server)
    _comparison_reply(resp, req_obj)


def test_pool_restart_cancel(
        sdk_pool_handle, sdk_wallet_trustee, looper, tconf):
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
        SCHEDULE: str(start_at)
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                       sdk_pool_handle,
                                       sdk_wallet_trustee,
                                       req_obj)
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: CANCEL,
        SCHEDULE: str(datetime.isoformat(start_at))
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    req_json, resp = sdk_get_reply(looper, req, 100)
    _stopServer(server)
    _comparison_reply(resp, req_obj)


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
        assert "Timeout" in ex.args[0]
    _stopServer(server)
    if is_reply_received:
        _comparison_reply(resp, req_obj)


def _comparison_reply(resp, req_obj):
    assert resp[f.RESULT.nm][f.MSG.nm] is None
    assert resp["op"] == REPLY
    assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj.identifier
    assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj.reqId
    assert resp[f.RESULT.nm][f.IS_SUCCESS.nm]

