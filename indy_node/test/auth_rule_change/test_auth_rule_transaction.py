import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, \
    ConstraintsEnum, ROLE, AUTH_CONSTRAINTS
from indy_common.constants import AUTH_RULE, NYM, TRUST_ANCHOR, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE
from indy_common.types import ConstraintEntityField
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_action=ADD_PREFIX, auth_type=NYM,
                                         field=ROLE, new_value=TRUST_ANCHOR,
                                         old_value=None, constraint=None):
    constraint = _generate_constraint_entity() \
        if constraint is None \
        else constraint
    op = {TXN_TYPE: AUTH_RULE,
          CONSTRAINT: constraint,
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


def test_auth_rule_transaction(looper,
                               sdk_wallet_trustee,
                               sdk_pool_handle):
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_wallet_trustee,
                                         sdk_pool_handle,
                                         auth_action=ADD_PREFIX,
                                         auth_type=NYM,
                                         field=ROLE,
                                         new_value='*'
                                         )


def test_auth_rule_transaction_with_large_constraint(looper,
                                                     sdk_wallet_trustee,
                                                     sdk_pool_handle):
    constraint = _generate_constraint_list(auth_constraints=[_generate_constraint_entity(role=TRUSTEE),
                                                             _generate_constraint_entity(role=STEWARD)])
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_wallet_trustee,
                                         sdk_pool_handle,
                                         constraint=constraint)


def test_reject_auth_rule_transaction(looper,
                                      sdk_wallet_trust_anchor,
                                      sdk_pool_handle):
    with pytest.raises(RequestRejectedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trust_anchor,
                                             sdk_pool_handle)
    e.match('UnauthorizedClientRequest')
    e.match('can not do this action')


def test_reqnack_auth_rule_transaction_with_wrong_key(looper,
                                                      sdk_wallet_trustee,
                                                      sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             auth_type="*")
    e.match("InvalidClientRequest")
    e.match("is not contained in the authorization map")


def test_reqnack_auth_rule_edit_transaction_with_wrong_format(looper,
                                                              sdk_wallet_trustee,
                                                              sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             auth_action=EDIT_PREFIX)
    e.match("InvalidClientRequest")
    e.match("Transaction for change authentication "
            "rule for {}={} must contain field {}".
            format(AUTH_ACTION, EDIT_PREFIX, OLD_VALUE))


def test_reqnack_auth_rule_add_transaction_with_wrong_format(looper,
                                                             sdk_wallet_trustee,
                                                             sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             old_value="*")
    e.match("InvalidClientRequest")
    e.match("Transaction for change authentication "
            "rule for {}={} must not contain field {}".
            format(AUTH_ACTION, ADD_PREFIX, OLD_VALUE))


def _generate_constraint_entity(constraint_id=ConstraintsEnum.ROLE_CONSTRAINT_ID,
                                role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=False,
                                metadata=None):
    return {CONSTRAINT_ID: constraint_id,
            ROLE: role,
            SIG_COUNT: sig_count,
            NEED_TO_BE_OWNER: need_to_be_owner,
            METADATA: metadata}


def _generate_constraint_list(constraint_id=ConstraintsEnum.AND_CONSTRAINT_ID,
                              auth_constraints=None):
    auth_constraints = _generate_constraint_entity() \
        if auth_constraints is None \
        else auth_constraints
    return {CONSTRAINT_ID: constraint_id,
            AUTH_CONSTRAINTS: auth_constraints}
