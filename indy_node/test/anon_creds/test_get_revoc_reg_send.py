import json
import copy

from indy_node.test.anon_creds.helper import build_get_revoc_reg_entry
from plenum.common.util import get_utc_epoch
from plenum.test.helper import sdk_send_and_check
from indy_common.constants import TIMESTAMP, REVOC_REG_DEF_ID, VALUE, ACCUM
from plenum.common.constants import TXN_TIME
from plenum.common.types import f


def test_send_get_revoc_reg_later_then_first_entry(looper,
                            txnPoolNodeSet,
                            sdk_pool_handle,
                            send_revoc_reg_entry_by_default,
                            sdk_wallet_steward):
    rev_entry_req, reg_reply = send_revoc_reg_entry_by_default
    get_revoc_reg = build_get_revoc_reg_entry(looper, sdk_wallet_steward)
    get_revoc_reg['operation'][REVOC_REG_DEF_ID] = rev_entry_req['operation'][REVOC_REG_DEF_ID]
    get_revoc_reg['operation'][TIMESTAMP] = get_utc_epoch() + 1000
    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert rev_entry_req['operation'][REVOC_REG_DEF_ID] == reply['result'][REVOC_REG_DEF_ID]
    assert rev_entry_req['operation'][VALUE][ACCUM] == reply['result']['data'][VALUE][ACCUM]


def test_send_get_revoc_reg_earlier_then_first_entry(
        looper,
        txnPoolNodeSet,
        sdk_pool_handle,
        send_revoc_reg_entry_by_default,
        sdk_wallet_steward):
    rev_entry_req, reg_reply = send_revoc_reg_entry_by_default
    get_revoc_reg = build_get_revoc_reg_entry(looper, sdk_wallet_steward)
    get_revoc_reg['operation'][REVOC_REG_DEF_ID] = rev_entry_req['operation'][REVOC_REG_DEF_ID]
    get_revoc_reg['operation'][TIMESTAMP] = get_utc_epoch() - 1000

    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert reply['result']['data'] is None
    assert reply['result'][TXN_TIME] is None
    assert reply['result'][f.SEQ_NO.nm] is None
