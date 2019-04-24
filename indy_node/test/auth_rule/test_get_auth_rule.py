import pytest

from indy_common.state import config
from plenum.common.types import OPERATION

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import ROLE
from indy_common.authorize.auth_map import auth_map
from indy_common.constants import NYM, TRUST_ANCHOR, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE, GET_AUTH_RULE
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.test.auth_rule.helper import generate_constraint_list, generate_constraint_entity, \
    sdk_send_and_check_auth_rule_request
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD, DATA, STATE_PROOF
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_get_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle, key=None):
    op = {TXN_TYPE: GET_AUTH_RULE}
    if key:
        op.update(key)
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


def generate_key(auth_action=ADD_PREFIX, auth_type=NYM,
                 field=ROLE, new_value=TRUST_ANCHOR,
                 old_value=None):
    key = {AUTH_ACTION: auth_action,
           AUTH_TYPE: auth_type,
           FIELD: field,
           NEW_VALUE: new_value,
           }
    if old_value:
        key[OLD_VALUE] = old_value
    return key


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


def test_get_one_auth_rule_transaction(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    key = generate_key()
    str_key = ConfigReqHandler.get_auth_key(key)
    req, resp = sdk_get_auth_rule_request(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          key)[0]
    assert auth_map.get(str_key).as_dict == \
           resp["result"][DATA][config.make_state_path_for_auth_rule(str_key).decode()]


def test_get_all_auth_rule_transactions(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle):
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)

    expect = {config.make_state_path_for_auth_rule(key).decode(): constraint.as_dict
              for key, constraint in auth_map.items()}
    result = resp[0][1]["result"][DATA]
    assert result == expect


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
    str_key = ConfigReqHandler.get_auth_key(dict_auth_key)
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle,
                                     dict_auth_key)
    print(config.make_state_path_for_auth_rule(str_key))
    result = resp[0][1]["result"][DATA][config.make_state_path_for_auth_rule(str_key).decode()]
    assert result == constraint
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
    auth_key = ConfigReqHandler.get_auth_key(resp[0][0][OPERATION])
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)
    expect = {config.make_state_path_for_auth_rule(key).decode(): constraint.as_dict
              for key, constraint in auth_map.items()}
    expect[config.make_state_path_for_auth_rule(auth_key).decode()] = constraint
    result = resp[0][1]["result"][DATA]
    assert result == expect
