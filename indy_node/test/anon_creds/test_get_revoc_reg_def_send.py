import json
import time
from indy_common.constants import CRED_DEF_ID, ID, REVOC_TYPE, TAG, GET_REVOC_REG_DEF, VALUE, MAX_CRED_NUM, TXN_TYPE
from indy_common.state import domain
from indy_common.types import Request
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.test.helper import sdk_send_and_check


def compare_request_reply(req, reply):
    assert req['operation'][CRED_DEF_ID] == reply['result']['data'][CRED_DEF_ID]
    assert req['operation'][ID] == reply['result']['data'][ID]
    assert req['operation'][TAG] == reply['result']['data'][TAG]
    assert req['operation'][VALUE] == reply['result']['data'][VALUE]


def test_send_get_revoc_reg_def(looper,
                                txnPoolNodeSet,
                                sdk_wallet_steward,
                                sdk_pool_handle,
                                send_revoc_reg_def_by_default):
    _, author_did = sdk_wallet_steward
    revoc_req, _ = send_revoc_reg_def_by_default
    revoc_reg_def_id = revoc_req['operation'][ID]
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
    replies = sdk_send_and_check([json.dumps(get_revoc_reg_def_req)],
                                 looper,
                                 txnPoolNodeSet,
                                 sdk_pool_handle)
    req, reply = replies[0]
    compare_request_reply(revoc_req, reply)


def test_get_revoc_reg_def_from_uncommited(looper,
                                           txnPoolNodeSet,
                                           sdk_wallet_steward,
                                           sdk_pool_handle,
                                           send_revoc_reg_def_by_default):
    # REVOC_REG_DEF was added into pool by send_revoc_reg_def_by_default fixture

    _, author_did = sdk_wallet_steward
    revoc_req, _ = send_revoc_reg_def_by_default
    new_maxCredNum = 100
    revoc_req['operation'][VALUE][MAX_CRED_NUM] = new_maxCredNum
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_req['operation'])

    # We apply transacttion, which will be not commited

    for node in txnPoolNodeSet:
        node.write_manager.apply_request(Request(**revoc_req), int(time.time()))
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

    # Send GET_REVOC_REG_DEF query.
    # We expects that commited REVOC_REG_DEF transaction will be returned

    replies = sdk_send_and_check([json.dumps(get_revoc_reg_def_req)],
                                 looper,
                                 txnPoolNodeSet,
                                 sdk_pool_handle)
    req, reply = replies[0]
    assert new_maxCredNum != reply['result']['data'][VALUE][MAX_CRED_NUM]
