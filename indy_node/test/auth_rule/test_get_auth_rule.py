import pytest

from plenum.common.types import OPERATION

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE
from indy_common.authorize.auth_map import auth_map
from indy_common.constants import NYM, TRUST_ANCHOR, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE, SCHEMA, CONSTRAINT, AUTH_RULE
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.test.auth_rule.helper import generate_constraint_list, generate_constraint_entity, \
    sdk_send_and_check_auth_rule_request, generate_key, sdk_get_auth_rule_request
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD, DATA, STATE_PROOF
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies

RESULT = "result"


def test_fail_get_auth_rule_with_incorrect_key(looper,
                                               sdk_wallet_trustee,
                                               sdk_pool_handle):
    key = generate_key()
    key[AUTH_TYPE] = "wrong_txn_type"
    with pytest.raises(RequestNackedException, match="Unknown authorization rule: key .* "
                                                     "is not found in authorization map."):
        sdk_get_auth_rule_request(looper,
                                  sdk_wallet_trustee,
                                  sdk_pool_handle,
                                  key)[0]

    del key[AUTH_TYPE]
    with pytest.raises(RequestNackedException, match="Not enough fields to build an auth key."):
        sdk_get_auth_rule_request(looper,
                                  sdk_wallet_trustee,
                                  sdk_pool_handle,
                                  key)[0]


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
    str_key = ConfigReqHandler.get_auth_key(key)
    req, resp = sdk_get_auth_rule_request(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          key)[0]
    for resp_rule in resp[RESULT][DATA]:
        _check_key(key, resp_rule)
        assert auth_map.get(str_key).as_dict == resp_rule[CONSTRAINT]


def test_get_one_disabled_auth_rule_transaction(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle):
    key = generate_key(auth_action=EDIT_PREFIX, auth_type=SCHEMA,
                       field='*', old_value='*', new_value='*')
    req, resp = sdk_get_auth_rule_request(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          key)[0]
    result = resp["result"][DATA]
    assert len(result) == 1
    _check_key(key, result[0])
    assert {} == result[0][CONSTRAINT]


def test_get_all_auth_rule_transactions(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle):
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)

    result = resp[0][1]["result"][DATA]
    for i, (auth_key, constraint) in enumerate(auth_map.items()):
        rule = result[i]
        assert auth_key == ConfigReqHandler.get_auth_key(rule)
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
    new_value = TRUST_ANCHOR
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    resp = sdk_send_and_check_auth_rule_request(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle,
                                                auth_action=auth_action, auth_type=auth_type,
                                                field=field, new_value=new_value,
                                                constraint=constraint)
    dict_auth_key = generate_key(auth_action=auth_action, auth_type=auth_type,
                                 field=field, new_value=new_value)
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     dict_auth_key)
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
    new_value = TRUST_ANCHOR
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    resp = sdk_send_and_check_auth_rule_request(looper,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle,
                                                auth_action=auth_action, auth_type=auth_type,
                                                field=field, new_value=new_value,
                                                constraint=constraint)
    str_auth_key = ConfigReqHandler.get_auth_key(resp[0][0][OPERATION])
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)

    result = resp[0][1]["result"][DATA]
    for rule in result:
        key = ConfigReqHandler.get_auth_key(rule)
        if auth_map[key] is None:
            assert {} == rule[CONSTRAINT]
        elif key == str_auth_key:
            assert constraint == rule[CONSTRAINT]
        else:
            assert auth_map[key].as_dict == rule[CONSTRAINT]


def test_auth_rule_after_get_auth_rule_without_changes(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    # get all auth rules
    auth_rules = sdk_get_auth_rule_request(looper,
                                           sdk_wallet_trustee,
                                           sdk_pool_handle)

    # prepare action key
    dict_key = dict(auth_rules[0][1][RESULT][DATA][0])
    dict_key.pop(CONSTRAINT)

    # prepare "operation" to send AUTH_RULE txn
    op = dict(auth_rules[0][1][RESULT][DATA][0])
    op[TXN_TYPE] = AUTH_RULE

    # send AUTH_RULE txn
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    sdk_get_and_check_replies(looper, [req])

    # send GET_AUTH_RULE
    get_response = sdk_get_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             dict_key)

    # check response
    result = get_response[0][1]["result"][DATA]
    assert len(result) == 1
    _check_key(dict_key, result[0])
    assert auth_rules[0][1][RESULT][DATA][0][CONSTRAINT] == result[0][CONSTRAINT]
    assert get_response[0][1]["result"][STATE_PROOF]


def test_auth_rule_after_get_auth_rule(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    # get all auth rules
    auth_rules = sdk_get_auth_rule_request(looper,
                                           sdk_wallet_trustee,
                                           sdk_pool_handle)

    # prepare action key
    dict_key = dict(auth_rules[0][1][RESULT][DATA][0])
    dict_key.pop(CONSTRAINT)

    # prepare "operation" to send AUTH_RULE txn
    op = dict(auth_rules[0][1][RESULT][DATA][0])
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
    get_response = sdk_get_auth_rule_request(looper,
                                             sdk_wallet_trustee,
                                             sdk_pool_handle,
                                             dict_key)

    # check response
    result = get_response[0][1]["result"][DATA]
    assert len(result) == 1
    _check_key(dict_key, result[0])
    assert constraint == result[0][CONSTRAINT]
    assert get_response[0][1]["result"][STATE_PROOF]
