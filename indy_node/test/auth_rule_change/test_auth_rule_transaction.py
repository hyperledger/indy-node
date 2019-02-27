import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE
from indy_common.constants import NYM, TRUST_ANCHOR, AUTH_ACTION, OLD_VALUE
from indy_node.test.auth_rule_change.helper import generate_constraint_entity, generate_constraint_list, \
    generate_auth_rule_operation
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_action=ADD_PREFIX, auth_type=NYM,
                                         field=ROLE, new_value=TRUST_ANCHOR,
                                         old_value=None, constraint=None):
    op = generate_auth_rule_operation(auth_action, auth_type,
                                      field, new_value,
                                      old_value, constraint)

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


def test_auth_rule_transaction_with_large_constraint(looper,
                                                     sdk_wallet_trustee,
                                                     sdk_pool_handle):
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                             generate_constraint_entity(role=STEWARD)])
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
    e.match("is not found in authorization map")


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
