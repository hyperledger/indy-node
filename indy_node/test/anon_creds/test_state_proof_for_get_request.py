import json
import copy
from indy_common.constants import CRED_DEF_ID, ID, REVOC_TYPE, TAG, GET_REVOC_REG_DEF, \
    TXN_TYPE, TIMESTAMP, REVOC_REG_DEF_ID, VALUE, FROM, TO, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM
from plenum.common.constants import STATE_PROOF
from indy_common.state import domain
from plenum.common.txn_util import get_txn_time
from plenum.common.util import randomString
from indy_node.test.anon_creds.helper import check_valid_proof, build_get_revoc_reg_delta, build_get_revoc_reg_entry
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.test.helper import sdk_send_and_check
from plenum.common.util import get_utc_epoch


def test_state_proof_returned_for_get_revoc_reg_def(looper,
                                                    txnPoolNodeSet,
                                                    sdk_wallet_steward,
                                                    sdk_pool_handle,
                                                    send_revoc_reg_def_by_default):
    _, author_did = sdk_wallet_steward
    revoc_req, _ = send_revoc_reg_def_by_default
    get_revoc_reg_def_req = {
        ID: ":".join([author_did,
                      domain.MARKER_REVOC_DEF,
                      revoc_req['operation'][CRED_DEF_ID],
                      revoc_req['operation'][REVOC_TYPE],
                      revoc_req['operation'][TAG]]),
        TXN_TYPE: GET_REVOC_REG_DEF,
    }
    get_revoc_reg_def_req = sdk_sign_request_from_dict(looper,
                                                       sdk_wallet_steward,
                                                       get_revoc_reg_def_req)
    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg_def_req)],
                                 looper,
                                 txnPoolNodeSet,
                                 sdk_pool_handle)
    reply = sdk_reply[0][1]
    check_valid_proof(reply)


def test_state_proof_returned_for_get_revoc_reg(looper,
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
    check_valid_proof(reply)


def test_state_proof_returned_for_get_revoc_reg_delta(looper,
                                                      txnPoolNodeSet,
                                                      sdk_pool_handle,
                                                      sdk_wallet_steward,
                                                      send_revoc_reg_entry_by_default):
    # We save timestamp of state changes.
    # looper and txnPoolNodeSet has "module" scope, therefore,
    # when we send request with FROM section, it's not a clean situation
    looper.runFor(3)
    # Assume, that send_revoc_reg_entry_by_default will add into revoked [1,2,3,4,5]
    rev_reg_req1, rev_reg_reply1 = send_revoc_reg_entry_by_default
    rev_reg_req1['operation'][VALUE][REVOKED] = []
    # Issue [1,2,3], Revoked now must be [4,5]
    rev_reg_req1['operation'][VALUE][ISSUED] = [1, 2, 3]
    rev_reg_req1['operation'][VALUE][PREV_ACCUM] = rev_reg_req1['operation'][VALUE][ACCUM]
    rev_reg_req1['operation'][VALUE][ACCUM] = randomString(10)
    rev_reg_req2, rev_reg_reply2 = sdk_send_and_check(
        [json.dumps(sdk_sign_request_from_dict(
            looper, sdk_wallet_steward, rev_reg_req1['operation']))],
        looper,
        txnPoolNodeSet,
        sdk_pool_handle)[0]
    # Revoke [10, 11]
    rev_reg_req2['operation'][VALUE][REVOKED] = [10, 11]
    rev_reg_req2['operation'][VALUE][ISSUED] = []
    rev_reg_req2['operation'][VALUE][PREV_ACCUM] = rev_reg_req2['operation'][VALUE][ACCUM]
    rev_reg_req2['operation'][VALUE][ACCUM] = randomString(10)
    rev_reg_req3, rev_reg_reply3 = sdk_send_and_check(
        [json.dumps(sdk_sign_request_from_dict(
            looper, sdk_wallet_steward, rev_reg_req2['operation']))],
        looper,
        txnPoolNodeSet,
        sdk_pool_handle)[0]
    reg_delta_req = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    reg_delta_req['operation'][REVOC_REG_DEF_ID] = rev_reg_req1['operation'][REVOC_REG_DEF_ID]
    reg_delta_req['operation'][FROM] = get_txn_time(rev_reg_reply1['result'])
    reg_delta_req['operation'][TO] = get_txn_time(rev_reg_reply3['result']) + 1000
    sdk_reply = sdk_send_and_check([json.dumps(reg_delta_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    check_valid_proof(reply)


def test_state_proof_returned_for_get_revoc_reg_delta_with_only_to(
                                                      looper,
                                                      txnPoolNodeSet,
                                                      sdk_pool_handle,
                                                      sdk_wallet_steward,
                                                      send_revoc_reg_entry_by_default):
    rev_reg_req, rev_reg_reply = send_revoc_reg_entry_by_default
    reg_delta_req = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    del reg_delta_req['operation'][FROM]
    reg_delta_req['operation'][REVOC_REG_DEF_ID] = rev_reg_req['operation'][REVOC_REG_DEF_ID]
    reg_delta_req['operation'][TO] = get_utc_epoch() + 1000
    sdk_reply = sdk_send_and_check([json.dumps(reg_delta_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    check_valid_proof(reply)


def test_state_proof_returned_for_delta_with_None_reply(
                                                      looper,
                                                      txnPoolNodeSet,
                                                      sdk_pool_handle,
                                                      sdk_wallet_steward,
                                                      send_revoc_reg_entry_by_default):
    rev_reg_req, rev_reg_reply = send_revoc_reg_entry_by_default
    reg_delta_req = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    del reg_delta_req['operation'][FROM]
    reg_delta_req['operation'][REVOC_REG_DEF_ID] = rev_reg_req['operation'][REVOC_REG_DEF_ID]
    reg_delta_req['operation'][TO] = get_utc_epoch() - 1000
    sdk_reply = sdk_send_and_check([json.dumps(reg_delta_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert STATE_PROOF not in reply['result']


def test_state_proof_returned_for_delta_with_from_earlier(
                                                      looper,
                                                      txnPoolNodeSet,
                                                      sdk_pool_handle,
                                                      sdk_wallet_steward,
                                                      send_revoc_reg_entry_by_default):
    rev_reg_req, rev_reg_reply = send_revoc_reg_entry_by_default
    reg_delta_req = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    reg_delta_req['operation'][FROM] = get_utc_epoch() - 1000
    reg_delta_req['operation'][REVOC_REG_DEF_ID] = rev_reg_req['operation'][REVOC_REG_DEF_ID]
    reg_delta_req['operation'][TO] = get_utc_epoch() + 1000
    sdk_reply = sdk_send_and_check([json.dumps(reg_delta_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    check_valid_proof(reply)
