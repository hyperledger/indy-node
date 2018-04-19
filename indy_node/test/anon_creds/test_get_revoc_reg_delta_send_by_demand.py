import json
import copy
from plenum.common.util import get_utc_epoch
from plenum.test.helper import sdk_send_and_check, sdk_sign_request_from_dict
from indy_common.constants import REVOC_REG_DEF_ID, VALUE, FROM, TO, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, STATE_PROOF_FROM, ACCUM_TO, ACCUM_FROM, REVOC_TYPE
from plenum.common.constants import TXN_TIME, DATA
from plenum.common.types import f
from plenum.common.util import randomString


def test_send_with_only_to_by_demand(looper,
                            txnPoolNodeSet,
                            sdk_pool_handle,
                            send_revoc_reg_entry_by_demand,
                            build_get_revoc_reg_delta):
    rev_entry_req, reg_reply = send_revoc_reg_entry_by_demand
    get_revoc_reg_delta = copy.deepcopy(build_get_revoc_reg_delta)
    del get_revoc_reg_delta['operation'][FROM]
    get_revoc_reg_delta['operation'][REVOC_REG_DEF_ID] = rev_entry_req['operation'][REVOC_REG_DEF_ID]
    get_revoc_reg_delta['operation'][TO] = get_utc_epoch() + 1000
    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg_delta)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert rev_entry_req['operation'][REVOC_REG_DEF_ID] == reply['result'][REVOC_REG_DEF_ID]
    assert rev_entry_req['operation'][VALUE][ACCUM] == reply['result'][DATA][VALUE][ACCUM_TO][VALUE][ACCUM]
    assert rev_entry_req['operation'][VALUE][ISSUED] == reply['result'][DATA][VALUE][ISSUED]


def test_send_earlier_then_first_entry_by_demand(
        looper,
        txnPoolNodeSet,
        sdk_pool_handle,
        send_revoc_reg_entry_by_demand,
        build_get_revoc_reg_delta):
    rev_entry_req, reg_reply = send_revoc_reg_entry_by_demand
    get_revoc_reg_delta = copy.deepcopy(build_get_revoc_reg_delta)
    del get_revoc_reg_delta['operation'][FROM]
    get_revoc_reg_delta['operation'][REVOC_REG_DEF_ID] = rev_entry_req['operation'][REVOC_REG_DEF_ID]
    get_revoc_reg_delta['operation'][TO] = get_utc_epoch() - 1000
    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg_delta)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert reply['result'][DATA][REVOC_REG_DEF_ID] == rev_entry_req['operation'][REVOC_REG_DEF_ID]
    assert VALUE not in reply['result'][DATA]
    assert REVOC_TYPE not in reply['result'][DATA]
    assert reply['result'][f.SEQ_NO.nm] is None
    assert reply['result'][TXN_TIME] is None


def test_send_with_from_by_demand(looper,
        txnPoolNodeSet,
        sdk_pool_handle,
        sdk_wallet_steward,
        send_revoc_reg_entry_by_demand,
        build_get_revoc_reg_delta):
    # We save timestamp of state changes.
    # looper and txnPoolNodeSet has "module", therefore,
    # when we send request with FROM section, it's not a clean situation
    looper.runFor(3)
    # Assume, that send_revoc_reg_entry_by_demand will add into issued [1,2,3,4,5]
    rev_reg_req1, rev_reg_reply1 = send_revoc_reg_entry_by_demand
    rev_reg_req1['operation'][VALUE][ISSUED] = []
    # Revoked [1,2,3], Issued now must be [4,5]
    rev_reg_req1['operation'][VALUE][REVOKED] = [1, 2, 3]
    rev_reg_req1['operation'][VALUE][PREV_ACCUM] = rev_reg_req1['operation'][VALUE][ACCUM]
    rev_reg_req1['operation'][VALUE][ACCUM] = randomString(10)
    rev_reg_req2, rev_reg_reply2 = sdk_send_and_check(
        [json.dumps(sdk_sign_request_from_dict(
            looper, sdk_wallet_steward, rev_reg_req1['operation']))],
        looper,
        txnPoolNodeSet,
        sdk_pool_handle)[0]
    # Issued [10, 11]
    rev_reg_req2['operation'][VALUE][ISSUED] = [10, 11]
    rev_reg_req2['operation'][VALUE][REVOKED] = []
    rev_reg_req2['operation'][VALUE][PREV_ACCUM] = rev_reg_req2['operation'][VALUE][ACCUM]
    rev_reg_req2['operation'][VALUE][ACCUM] = randomString(10)
    rev_reg_req3, rev_reg_reply3 = sdk_send_and_check(
        [json.dumps(sdk_sign_request_from_dict(
            looper, sdk_wallet_steward, rev_reg_req2['operation']))],
        looper,
        txnPoolNodeSet,
        sdk_pool_handle)[0]
    reg_delta_req = copy.deepcopy(build_get_revoc_reg_delta)
    reg_delta_req['operation'][REVOC_REG_DEF_ID] = rev_reg_req1['operation'][REVOC_REG_DEF_ID]
    reg_delta_req['operation'][FROM] = rev_reg_reply1['result'][TXN_TIME]
    reg_delta_req['operation'][TO] = rev_reg_reply3['result'][TXN_TIME] + 1000
    get_reply = sdk_send_and_check([json.dumps(reg_delta_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0][1]
    assert get_reply['result'][DATA][STATE_PROOF_FROM]
    assert get_reply['result'][DATA][VALUE][REVOKED] == [1, 2, 3]
    assert get_reply['result'][DATA][VALUE][ISSUED] == [10, 11]
    assert get_reply['result'][DATA][VALUE][ACCUM_TO][VALUE][ACCUM] == rev_reg_req3['operation'][VALUE][ACCUM]
    assert get_reply['result'][DATA][VALUE][ACCUM_FROM][VALUE][ACCUM] == rev_reg_reply1['result'][VALUE][ACCUM]
