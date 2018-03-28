from datetime import datetime, timedelta

import dateutil

from indy_common.constants import POOL_RESTART, ACTION, START, SCHEDULE
from plenum.common.constants import REPLY, TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply


def test_pool_restart(
        sdk_pool_handle, sdk_wallet_trustee, looper):

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
    req_json, resp = sdk_get_reply(looper, req, 100)
    assert resp[f.RESULT.nm][f.MSG.nm] is None
    assert resp["op"] == REPLY
    assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj.identifier
    assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj.reqId
    assert resp[f.RESULT.nm][f.IS_SUCCESS.nm]


