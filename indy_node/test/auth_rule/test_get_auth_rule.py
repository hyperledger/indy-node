import pytest

from indy_common.state import config
from indy_common.types import AuthRuleField
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.types import OPERATION
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD, DATA, STATE_PROOF
from plenum.common.exceptions import RequestNackedException

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE, AuthConstraintForbidden
from indy_common.authorize.auth_map import auth_map
from indy_common.constants import NYM, ENDORSER, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE, SCHEMA, CONSTRAINT, AUTH_RULE

from plenum.test.helper import (
    sdk_gen_request, sdk_sign_and_submit_req, sdk_get_and_check_replies,
    sdk_sign_and_submit_req_obj
)
from indy_node.test.helper import build_auth_rule_request_json, generate_constraint_entity
from indy_node.test.auth_rule.helper import generate_constraint_list, \
    sdk_send_and_check_auth_rule_request, generate_key, sdk_send_and_check_get_auth_rule_request, \
    sdk_send_and_check_get_auth_rule_invalid_request


RESULT = "result"


def test_fail_get_auth_rule_with_incorrect_key(looper,
                                               sdk_wallet_trustee,
                                               sdk_pool_handle):
    key = generate_key()
    key[AUTH_TYPE] = "wrong_txn_type"
    with pytest.raises(RequestNackedException, match="Unknown authorization rule: key .* "
                                                     "is not found in authorization map."):
        sdk_send_and_check_get_auth_rule_invalid_request(
            looper, sdk_pool_handle, sdk_wallet_trustee, **key
        )[0]

    del key[AUTH_TYPE]
    with pytest.raises(RequestNackedException, match="Not enough fields to build an auth key."):
        sdk_send_and_check_get_auth_rule_invalid_request(
            looper, sdk_pool_handle, sdk_wallet_trustee, **key
        )[0]


def _check_key(key, resp_key):
    assert key[AUTH_ACTION] in resp_key[AUTH_ACTION]
    assert key[AUTH_TYPE] in resp_key[AUTH_TYPE]
    assert key[FIELD] in resp_key[FIELD]
    assert key[NEW_VALUE] in resp_key[NEW_VALUE]
    if key[AUTH_ACTION] == EDIT_PREFIX:
        assert key[OLD_VALUE] in resp_key[OLD_VALUE]
    else:
        assert OLD_VALUE not in resp_key


def test_get_one_auth_rule_transaction(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    key = generate_key()
    str_key = StaticAuthRuleHelper.get_auth_key(key)
    req, resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee, **key
    )[0]

    for resp_rule in resp[RESULT][DATA]:
        _check_key(key, resp_rule)
        assert auth_map.get(str_key).as_dict == resp_rule[CONSTRAINT]


def test_get_unknown_auth_rule_transaction_is_rejected(
    looper, sdk_wallet_trustee, sdk_pool_handle
):
    key = generate_key(auth_action=ADD_PREFIX, auth_type=NYM,
                       field=ROLE, new_value='*')
    with pytest.raises(
        RequestNackedException,
        match=r"Unknown authorization rule: key '1--ADD--role--\*--\*' "
              "is not found in authorization map"
    ):
        sdk_send_and_check_get_auth_rule_request(
            looper, sdk_pool_handle, sdk_wallet_trustee, **key
        )


def test_get_one_disabled_auth_rule_transaction(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle):
    key = generate_key(auth_action=EDIT_PREFIX, auth_type=SCHEMA,
                       field='*', old_value='*', new_value='*')
    req, resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee, **key
    )[0]

    result = resp["result"][DATA]
    assert len(result) == 1
    _check_key(key, result[0])
    assert AuthConstraintForbidden().as_dict == result[0][CONSTRAINT]


def test_get_all_auth_rule_transactions(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle):
    resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )

    result = resp[0][1]["result"][DATA]
    for i, (auth_key, constraint) in enumerate(auth_map.items()):
        rule = result[i]
        assert auth_key == StaticAuthRuleHelper.get_auth_key(rule)
        if constraint is None:
            assert {} == rule[CONSTRAINT]
        else:
            assert constraint.as_dict == rule[CONSTRAINT]


def test_get_one_auth_rule_transaction_after_write(looper,
                                                   sdk_wallet_trustee,
                                                   sdk_pool_handle):
    auth_action = ADD_PREFIX
    auth_type = NYM
    field = ROLE
    new_value = ENDORSER
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    resp = sdk_send_and_check_auth_rule_request(looper,
                                                sdk_pool_handle,
                                                sdk_wallet_trustee,
                                                auth_action=auth_action, auth_type=auth_type,
                                                field=field, new_value=new_value,
                                                constraint=constraint)
    dict_auth_key = generate_key(auth_action=auth_action, auth_type=auth_type,
                                 field=field, new_value=new_value)
    resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee, **dict_auth_key
    )
    result = resp[0][1]["result"][DATA]
    assert len(result) == 1
    _check_key(dict_auth_key, result[0])
    assert constraint == result[0][CONSTRAINT]
    assert resp[0][1]["result"][STATE_PROOF]


def test_get_all_auth_rule_transactions_after_write(looper,
                                                    sdk_wallet_trustee,
                                                    sdk_pool_handle):
    auth_action = ADD_PREFIX
    auth_type = NYM
    field = ROLE
    new_value = ENDORSER
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    resp = sdk_send_and_check_auth_rule_request(looper,
                                                sdk_pool_handle,
                                                sdk_wallet_trustee,
                                                auth_action=auth_action,
                                                auth_type=auth_type,
                                                field=field,
                                                new_value=new_value,
                                                constraint=constraint)
    str_auth_key = StaticAuthRuleHelper.get_auth_key(resp[0][0][OPERATION])
    resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )

    result = resp[0][1]["result"][DATA]
    for rule in result:
        key = StaticAuthRuleHelper.get_auth_key(rule)
        if key == str_auth_key:
            assert constraint == rule[CONSTRAINT]
        else:
            assert auth_map[key].as_dict == rule[CONSTRAINT]


def test_auth_rule_after_get_auth_rule_as_is(
    looper, sdk_pool_handle, sdk_wallet_trustee
):
    # get all auth rules
    auth_rules_resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )
    auth_rules = auth_rules_resp[0][1][RESULT][DATA]

    for rule in auth_rules:
        # prepare action key
        dict_key = dict(rule)
        dict_key.pop(CONSTRAINT)

        # prepare "operation" to send AUTH_RULE txn
        op = dict(rule)
        op[TXN_TYPE] = AUTH_RULE

        # send AUTH_RULE txn
        req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
        req = sdk_sign_and_submit_req_obj(looper,
                                          sdk_pool_handle,
                                          sdk_wallet_trustee,
                                          req_obj)
        sdk_get_and_check_replies(looper, [req])

        # send GET_AUTH_RULE
        get_response = sdk_send_and_check_get_auth_rule_request(
            looper, sdk_pool_handle, sdk_wallet_trustee, **dict_key)
        # check response
        result = get_response[0][1]["result"][DATA]
        assert len(result) == 1
        _check_key(dict_key, result[0])
        assert rule[CONSTRAINT] == result[0][CONSTRAINT]
        assert get_response[0][1]["result"][STATE_PROOF]


def test_auth_rule_after_get_auth_rule_as_is_using_sdk(
    looper, sdk_pool_handle, sdk_wallet_trustee
):
    # get all auth rules
    auth_rules_resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )
    auth_rules = auth_rules_resp[0][1][RESULT][DATA]

    for rule in auth_rules:
        # prepare action key
        dict_key = dict(rule)
        dict_key.pop(CONSTRAINT)

        # prepare AUTH_RULE request
        req_json = build_auth_rule_request_json(
            looper, sdk_wallet_trustee[1], **rule
        )

        # send AUTH_RULE txn
        req = sdk_sign_and_submit_req(sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_json)
        sdk_get_and_check_replies(looper, [req])

        # send GET_AUTH_RULE
        get_response = sdk_send_and_check_get_auth_rule_request(
            looper, sdk_pool_handle, sdk_wallet_trustee, **dict_key)
        # check response
        result = get_response[0][1]["result"][DATA]
        assert len(result) == 1
        _check_key(dict_key, result[0])
        assert rule[CONSTRAINT] == result[0][CONSTRAINT]
        assert get_response[0][1]["result"][STATE_PROOF]


def test_auth_rule_after_get_auth_rule_as_is_except_constraint(
    looper, sdk_wallet_trustee, sdk_pool_handle
):
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    # get all auth rules
    auth_rules_resp = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )
    auth_rules = auth_rules_resp[0][1][RESULT][DATA]
    rule = auth_rules[0]

    # prepare action key
    dict_key = dict(rule)
    dict_key.pop(CONSTRAINT)

    # prepare "operation" to send AUTH_RULE txn
    op = dict(rule)
    op[TXN_TYPE] = AUTH_RULE
    op[CONSTRAINT] = constraint

    # send AUTH_RULE txn
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    sdk_get_and_check_replies(looper, [req])

    # send GET_AUTH_RULE
    get_response = sdk_send_and_check_get_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee, **dict_key
    )

    # check response
    result = get_response[0][1]["result"][DATA]
    assert len(result) == 1
    _check_key(dict_key, result[0])
    assert constraint == result[0][CONSTRAINT]
    assert get_response[0][1]["result"][STATE_PROOF]
