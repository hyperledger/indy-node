import pytest
import json

from common.serializers.serialization import config_state_serializer
from indy_common.state import config
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.constants import TRUSTEE, STEWARD, DATA
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE, CONSTRAINT_ID, ConstraintsEnum, SIG_COUNT, NEED_TO_BE_OWNER, \
    METADATA, OFF_LEDGER_SIGNATURE
from indy_common.constants import AUTH_ACTION, OLD_VALUE, NYM, ENDORSER, CONFIG_LEDGER_ID, CONSTRAINT

from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies
from indy_node.test.auth_rule.helper import sdk_send_and_check_req_json, sdk_send_and_check_get_auth_rule_request
from indy_node.test.auth_rule.helper import (
    generate_constraint_entity, generate_constraint_list,
    sdk_send_and_check_auth_rule_request, generate_auth_rule_operation,
    generate_key,
    sdk_send_and_check_auth_rule_invalid_request
)


def test_auth_rule_transaction_for_edit(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle):
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX)


def test_auth_rule_transaction(looper,
                               sdk_wallet_trustee,
                               sdk_pool_handle):
    sdk_send_and_check_auth_rule_request(
        looper, sdk_pool_handle, sdk_wallet_trustee
    )


def test_auth_rule_transaction_with_large_constraint(looper,
                                                     sdk_wallet_trustee,
                                                     sdk_pool_handle):
    constraint = generate_constraint_list(auth_constraints=[generate_constraint_entity(role=TRUSTEE),
                                                            generate_constraint_entity(role=STEWARD)])
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         constraint=constraint)


def test_reject_with_unacceptable_role_in_constraint(looper,
                                                     sdk_wallet_trustee,
                                                     sdk_pool_handle):
    constraint = generate_constraint_entity()
    unacceptable_role = 'olololo'
    constraint[ROLE] = unacceptable_role
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             constraint=constraint)
    e.match('InvalidClientRequest')
    e.match('client request invalid')
    e.match('Role {} is not acceptable'.format(unacceptable_role))


def test_reject_auth_rule_transaction(looper,
                                      sdk_wallet_steward,
                                      sdk_pool_handle):
    with pytest.raises(RequestRejectedException) as e:
        sdk_send_and_check_auth_rule_request(
            looper, sdk_pool_handle, sdk_wallet_steward
        )
    e.match('Not enough TRUSTEE signatures')


def test_reqnack_auth_rule_transaction_with_wrong_key(looper,
                                                      sdk_wallet_trustee,
                                                      sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             auth_type="*")
    e.match('InvalidClientRequest')
    e.match("client request invalid")
    e.match("is not found in authorization map")


def test_reqnack_auth_rule_edit_transaction_with_wrong_format(looper,
                                                              sdk_wallet_trustee,
                                                              sdk_pool_handle):
    op = generate_auth_rule_operation(auth_action=EDIT_PREFIX)
    op.pop(OLD_VALUE)

    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req_json = json.dumps(req_obj.as_dict)
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_req_json(
            looper, sdk_pool_handle, sdk_wallet_trustee, req_json,
        )
    e.match('InvalidClientRequest')
    e.match("client request invalid")
    e.match("Transaction for change authentication "
            "rule for {}={} must contain field {}".
            format(AUTH_ACTION, EDIT_PREFIX, OLD_VALUE))


def test_reqnack_auth_rule_add_transaction_with_wrong_format(looper,
                                                             sdk_wallet_trustee,
                                                             sdk_pool_handle):
    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_auth_rule_invalid_request(
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            **generate_key(old_value="*")
        )
    e.match('InvalidClientRequest')
    e.match("client request invalid")
    e.match("Transaction for change authentication "
            "rule for {}={} must not contain field {}".
            format(AUTH_ACTION, ADD_PREFIX, OLD_VALUE))


@pytest.mark.parametrize("off_ledger_signature", [True, False])
def test_auth_rule_state_format(
    looper, sdk_pool_handle, sdk_wallet_trustee, txnPoolNodeSet, off_ledger_signature
):
    auth_action = ADD_PREFIX
    auth_type = NYM
    field = ROLE
    new_value = ENDORSER
    constraint = {CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
                  ROLE: "*",
                  SIG_COUNT: 1,
                  NEED_TO_BE_OWNER: False,
                  METADATA: {}}
    if off_ledger_signature:
        constraint[OFF_LEDGER_SIGNATURE] = off_ledger_signature
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=auth_action,
                                         auth_type=auth_type,
                                         field=field,
                                         new_value=new_value,
                                         constraint=constraint)
    state = txnPoolNodeSet[0].db_manager.get_database(CONFIG_LEDGER_ID).state
    key = generate_key(auth_action, auth_type, field, new_value)
    path = config.make_state_path_for_auth_rule(StaticAuthRuleHelper.get_auth_key(key))
    state_constraint = config_state_serializer.deserialize(state.get(path))
    assert state_constraint == constraint

    _, before_resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                              sdk_pool_handle,
                                                              sdk_wallet_trustee,
                                                              auth_type=auth_type,
                                                              auth_action=auth_action,
                                                              field=field,
                                                              new_value=new_value
                                                              )[0]

    for rule in before_resp["result"][DATA]:
        if rule[CONSTRAINT][CONSTRAINT_ID] == 'ROLE' and off_ledger_signature:
            assert OFF_LEDGER_SIGNATURE in rule[CONSTRAINT]
