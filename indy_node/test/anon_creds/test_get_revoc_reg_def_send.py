import json
from indy_common.constants import CRED_DEF_ID, ID, TYPE, TAG, GET_REVOC_REG_DEF
from indy_common.state import domain
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.test.helper import sdk_send_and_check

def test_send_get_revoc_reg_def(looper,
                                txnPoolNodeSet,
                                sdk_wallet_steward,
                                sdk_pool_handle,
                                send_claim_def,
                                build_revoc_def_by_default):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = ":".join([author_did,
                                                    domain.MARKER_CLAIM_DEF,
                                                    claim_def_req['operation']["signature_type"],
                                                    str(claim_def_req['operation']["ref"])])
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    revoc_reg_def_id = revoc_reg['operation'][ID]
    get_revoc_reg_def_req = {
        ID: ":".join([author_did,
                     domain.MARKER_REVOC_DEF,
                      revoc_reg['operation'][CRED_DEF_ID],
                      revoc_reg['operation'][TYPE],
                      revoc_reg['operation'][TAG]]),
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
