import json

import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE, SIG_COUNT
from indy_common.constants import AUTH_ACTION, OLD_VALUE, CONSTRAINT, NEW_VALUE, NYM, ENDORSER, GET_AUTH_RULE
from indy_node.test.auth_rule.helper import sdk_send_and_check_get_auth_rule_request, \
    sdk_send_and_check_auth_rules_request_invalid
from indy_node.test.helper import sdk_send_and_check_req_json, sdk_send_and_check_auth_rules_request, generate_auth_rule
from plenum.common.constants import TRUSTEE, STEWARD, DATA, TXN_TYPE
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request

RESULT = "result"


def _send_and_check_get_auth_rule(looper, sdk_pool_handle, sdk_wallet, key):
    op = {TXN_TYPE: GET_AUTH_RULE,
          **key}
    req_obj = sdk_gen_request(op, identifier=sdk_wallet[1])
    return sdk_send_and_check_req_json(
        looper, sdk_pool_handle, sdk_wallet, json.dumps(req_obj.as_dict)
    )


def test_auth_rules_transaction_without_changes(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle):
    before_resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                           sdk_pool_handle,
                                                           sdk_wallet_trustee)
    sdk_send_and_check_auth_rules_request(looper,
                                          sdk_pool_handle,
                                          sdk_wallet_trustee,
                                          rules=before_resp[0][1][RESULT][DATA])
    after_resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                          sdk_pool_handle,
                                                          sdk_wallet_trustee)
    assert before_resp[0][1]["result"][DATA] == after_resp[0][1]["result"][DATA]


def test_auth_rules_transaction(looper,
                                sdk_wallet_trustee,
                                sdk_pool_handle):
    rule = generate_auth_rule()
    key = dict(rule)
    key.pop(CONSTRAINT)
    sdk_send_and_check_auth_rules_request(looper,
                                          sdk_pool_handle,
                                          sdk_wallet_trustee,
                                          rules=[rule])
    after_resp = _send_and_check_get_auth_rule(looper,
                                               sdk_pool_handle,
                                               sdk_wallet_trustee,
                                               key)
    assert [rule] == after_resp[0][1]["result"][DATA]


def test_reject_all_rules_from_auth_rules_txn(looper,
                                              sdk_wallet_trustee,
                                              sdk_pool_handle):
    _, before_resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                              sdk_pool_handle,
                                                              sdk_wallet_trustee)[0]
    rules = [generate_auth_rule(ADD_PREFIX, NYM,
                                ROLE, "wrong_new_value"),
             generate_auth_rule(EDIT_PREFIX, NYM,
                                ROLE, ENDORSER, TRUSTEE)]
    with pytest.raises(RequestNackedException):
        sdk_send_and_check_auth_rules_request(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_trustee,
                                              rules=rules)
    _, after_resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                             sdk_pool_handle,
                                                             sdk_wallet_trustee)[0]
    assert before_resp["result"][DATA] == after_resp["result"][DATA]


def test_reject_with_empty_rules_list(looper,
                                      sdk_wallet_trustee,
                                      sdk_pool_handle):
    with pytest.raises(RequestNackedException,
                       match="InvalidClientRequest.*length should be at least 1"):
        sdk_send_and_check_auth_rules_request_invalid(looper,
                                                      sdk_pool_handle,
                                                      sdk_wallet_trustee,
                                                      rules=[])


def test_reject_with_unacceptable_role_in_constraint(looper,
                                                     sdk_wallet_trustee,
                                                     sdk_pool_handle):
    rule = generate_auth_rule()
    unacceptable_role = 'olololo'
    rule[CONSTRAINT][ROLE] = unacceptable_role
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rules_request(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_trustee,
                                              rules=[rule])
    e.match('InvalidClientRequest')
    e.match('Role {} is not acceptable'.format(unacceptable_role))


def test_reject_auth_rules_transaction(looper,
                                       sdk_wallet_steward,
                                       sdk_pool_handle):
    with pytest.raises(RequestRejectedException) as e:
        sdk_send_and_check_auth_rules_request(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_steward)
    e.match('Not enough TRUSTEE signatures')


def test_reqnack_auth_rules_transaction_with_wrong_key(looper,
                                                       sdk_wallet_trustee,
                                                       sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rules_request(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_trustee,
                                              [generate_auth_rule(auth_type="*")])
    e.match("InvalidClientRequest")
    e.match("is not found in authorization map")


def test_reqnack_auth_rules_edit_transaction_with_wrong_format(looper,
                                                               sdk_wallet_trustee,
                                                               sdk_pool_handle):
    rule = generate_auth_rule(auth_action=EDIT_PREFIX)
    rule.pop(OLD_VALUE)
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rules_request_invalid(looper,
                                                      sdk_pool_handle,
                                                      sdk_wallet_trustee,
                                                      rules=[rule])
    e.match("InvalidClientRequest")
    e.match("Transaction for change authentication "
            "rule for {}={} must contain field {}".
            format(AUTH_ACTION, EDIT_PREFIX, OLD_VALUE))


def test_reqnack_auth_rules_add_transaction_with_wrong_format(looper,
                                                              sdk_wallet_trustee,
                                                              sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rules_request_invalid(looper,
                                                      sdk_pool_handle,
                                                      sdk_wallet_trustee,
                                                      [generate_auth_rule(old_value="*")])
    e.match("InvalidClientRequest")
    e.match("Transaction for change authentication "
            "rule for {}={} must not contain field {}".
            format(AUTH_ACTION, ADD_PREFIX, OLD_VALUE))
