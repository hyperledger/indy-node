from datetime import datetime, timedelta

import dateutil

from indy_common.constants import START
from indy_node.server.restart_log import RestartLog
from indy_node.test.pool_restart.helper import _createServer, sdk_send_restart, _stopServer
from indy_node.test.pool_restart.test_pool_restart import _comparison_reply, _check_restart_log


def test_pool_restarts_one_by_one(
        sdk_pool_handle, sdk_wallet_trustee, looper, tconf, txnPoolNodeSet):
    server, indicator = looper.loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )

    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    first_start = str(datetime.isoformat(unow + timedelta(seconds=1000)))
    req_obj, resp = sdk_send_restart(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     action=START,
                                     datetime=first_start)

    second_start = str(datetime.isoformat(unow + timedelta(seconds=2000)))
    req_obj, resp = sdk_send_restart(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     action=START,
                                     datetime=second_start)
    _comparison_reply(resp, req_obj)
    tmp = txnPoolNodeSet[0].restarter._actionLog
    restart_log = []
    for a in tmp:
        restart_log.append(a)
    restart_log.reverse()
    _check_restart_log(restart_log[2], RestartLog.SCHEDULED, first_start)
    _check_restart_log(restart_log[1], RestartLog.CANCELLED)
    _check_restart_log(restart_log[0], RestartLog.SCHEDULED, second_start)
    _stopServer(server)