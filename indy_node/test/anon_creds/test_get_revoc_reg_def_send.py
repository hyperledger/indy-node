import json
import time
from indy_common.constants import CRED_DEF_ID, ID, TYPE, TAG, GET_REVOC_REG_DEF, VALUE, MAX_CRED_NUM
from indy_common.state import domain
from indy_common.types import Request
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.test.helper import sdk_send_and_check


def test_send_get_revoc_reg_def(looper,
                                txnPoolNodeSet,
                                sdk_wallet_steward,
                                sdk_pool_handle,
                                send_revoc_reg_def):
    _, author_did = sdk_wallet_steward
    revoc_req = send_revoc_reg_def
    revoc_reg_def_id = revoc_req['operation'][ID]
    get_revoc_reg_def_req = {
        ID: ":".join([author_did,
                      domain.MARKER_REVOC_DEF,
                      revoc_req['operation'][CRED_DEF_ID],
                      revoc_req['operation'][TYPE],
                      revoc_req['operation'][TAG]]),
        TYPE: GET_REVOC_REG_DEF,
    }
    get_revoc_reg_def_req = sdk_sign_request_from_dict(looper,
                                                       sdk_wallet_steward,
                                                       get_revoc_reg_def_req)
    replies = sdk_send_and_check([json.dumps(get_revoc_reg_def_req)],
                                 looper,
                                 txnPoolNodeSet,
                                 sdk_pool_handle)
    req, reply = replies[0]
    assert revoc_reg_def_id == reply['result']['data'][ID]


def test_get_revoc_reg_def_from_uncommited(looper,
                                           txnPoolNodeSet,
                                           sdk_wallet_steward,
                                           sdk_pool_handle,
                                           send_revoc_reg_def):
    _, author_did = sdk_wallet_steward
    revoc_req = send_revoc_reg_def
    new_maxCredNum = 100
    # old_maxCredNum = revoc_req['operation'][VALUE][MAX_CRED_NUM]
    revoc_req['operation'][VALUE][MAX_CRED_NUM] = new_maxCredNum
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_req['operation'])
    for node in txnPoolNodeSet:
        node.getDomainReqHandler().apply(Request(**revoc_req), int(time.time()))
    get_revoc_reg_def_req = {
        ID: ":".join([author_did,
                      domain.MARKER_REVOC_DEF,
                      revoc_req['operation'][CRED_DEF_ID],
                      revoc_req['operation'][TYPE],
                      revoc_req['operation'][TAG]]),
        TYPE: GET_REVOC_REG_DEF,
    }
    get_revoc_reg_def_req = sdk_sign_request_from_dict(looper,
                                                       sdk_wallet_steward,
                                                       get_revoc_reg_def_req)
    replies = sdk_send_and_check([json.dumps(get_revoc_reg_def_req)],
                                 looper,
                                 txnPoolNodeSet,
                                 sdk_pool_handle)
    req, reply = replies[0]
    assert new_maxCredNum != reply['result']['data'][VALUE][MAX_CRED_NUM]
