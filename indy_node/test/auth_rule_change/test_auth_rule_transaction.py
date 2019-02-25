from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, ConstraintsEnum
from indy_common.constants import AUTH_RULE, SCHEMA, POOL_RESTART, NYM, TRUST_ANCHOR
from plenum.common.constants import TXN_TYPE, TRUSTEE, ROLE, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, OLD_VALUE, \
    NEW_VALUE
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_reply, sdk_get_and_check_replies


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle):
    op = {TXN_TYPE: AUTH_RULE,
          CONSTRAINT: None,
          AUTH_ACTION: ADD_PREFIX,
          AUTH_TYPE: NYM,
          FIELD: ROLE,
          NEW_VALUE: TRUST_ANCHOR
           }
    # op = {TXN_TYPE: POOL_RESTART,
    #       "action": "start",
    #       "timestamp": ""}
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


def test_auth_rule_transaction(looper,
                               sdk_wallet_trustee,
                               sdk_pool_handle):
    resp = sdk_send_and_check_auth_rule_request(looper,
                                                          sdk_wallet_trustee,
                                                          sdk_pool_handle)
