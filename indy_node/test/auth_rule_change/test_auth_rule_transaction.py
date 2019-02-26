import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, ConstraintsEnum
from indy_common.constants import AUTH_RULE, NYM, TRUST_ANCHOR
from plenum.common.constants import TXN_TYPE, TRUSTEE, ROLE, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, OLD_VALUE, \
    NEW_VALUE
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_action=ADD_PREFIX, auth_type=NYM,
                                         field=ROLE, new_value=TRUST_ANCHOR,
                                         old_value=None):
    op = {TXN_TYPE: AUTH_RULE,
          CONSTRAINT: {CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
                       ROLE: TRUSTEE,
                       SIG_COUNT: 1,
                       NEED_TO_BE_OWNER: False,
                       METADATA: {}},
          AUTH_ACTION: auth_action,
          AUTH_TYPE: auth_type,
          FIELD: field,
          NEW_VALUE: new_value
          }
    if old_value:
        op[OLD_VALUE] = old_value
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
    sdk_send_and_check_auth_rule_request(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle)


def test_reject_auth_rule_transaction(looper,
                                      sdk_wallet_trust_anchor,
                                      sdk_pool_handle):
    with pytest.raises(RequestRejectedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trust_anchor,
                                             sdk_pool_handle)
    e.match('UnauthorizedClientRequest')
    e.match('can not do this action')


def test_reqnack_auth_rule_transaction(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             auth_type="*")
    e.match("InvalidClientRequest")
    e.match("is not contained in the authorization map")
