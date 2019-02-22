from indy_common.constants import AUTH_RULE
from plenum.common.constants import TXN_TYPE, TRUSTEE, ROLE
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_reply, sdk_get_and_check_replies


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle):
    # op = {TXN_TYPE: AUTH_RULE,
    #       AUTH_CONSTRAINTS: {CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
    #                          ROLE: TRUSTEE,
    #                          SIG_COUNT: 1,
    #                          NEED_TO_BE_OWNER: False,
    #                          METADATA: {}
    #                          }
    #       }
    op = {TXN_TYPE: AUTH_RULE,
          AUTH_CONSTRAINTS: {CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
                             ROLE: TRUSTEE,
                             SIG_COUNT: 1,
                             NEED_TO_BE_OWNER: False,
                             METADATA: {}
                             }
          }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    req_json, resp = sdk_get_and_check_replies(looper, [req])
    return req_json, resp


def test_auth_rule_transaction(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle):
    req_json, resp = sdk_send_and_check_auth_rule_request(looper,
                                                                 sdk_wallet_trustee,
                                                                 sdk_pool_handle)


