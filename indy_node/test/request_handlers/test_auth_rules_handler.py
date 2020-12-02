import pytest
from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX

from indy_common.constants import OLD_VALUE, AUTH_TYPE, ROLE, ENDORSER, AUTH_ACTION, \
    AUTH_RULES, RULES
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler

from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rules_handler import AuthRulesHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from indy_node.test.auth_rule.helper import generate_auth_rule
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE, TXN_TYPE, STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, get_payload_data


@pytest.fixture(scope="module")
def auth_rules_handler(db_manager, write_auth_req_validator):
    return AuthRulesHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def auth_rules_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={TXN_TYPE: AUTH_RULES,
                              RULES: [generate_auth_rule()]})


def test_auth_rule_static_validation(auth_rules_request, auth_rules_handler: AuthRulesHandler):
    auth_rules_handler.static_validation(auth_rules_request)


def test_auth_rule_static_validation_failed_without_old_value(auth_rules_request,
                                                              auth_rules_handler: AuthRulesHandler):
    rule = auth_rules_request.operation[RULES][0]
    if OLD_VALUE in rule:
        del rule[OLD_VALUE]
    rule[AUTH_ACTION] = EDIT_PREFIX
    with pytest.raises(InvalidClientRequest, match="EDIT must contain field old_value"):
        auth_rules_handler.static_validation(auth_rules_request)


def test_auth_rule_static_validation_failed_with_excess_field(auth_rules_request,
                                                              auth_rules_handler: AuthRulesHandler):
    rule = auth_rules_request.operation[RULES][0]
    rule[OLD_VALUE] = "old_value"
    rule[AUTH_TYPE] = ADD_PREFIX
    with pytest.raises(InvalidClientRequest, match="ADD must not contain field old_value"):
        auth_rules_handler.static_validation(auth_rules_request)


def test_auth_rule_static_validation_failed_with_incorrect_key(auth_rules_request,
                                                               auth_rules_handler: AuthRulesHandler):
    auth_rules_request.operation[RULES].append(generate_auth_rule(auth_action=ADD_PREFIX,
                                                                 auth_type="wrong_type",
                                                                 field=ROLE, new_value=ENDORSER))
    with pytest.raises(InvalidClientRequest, match="key .* is not found in authorization map"):
        auth_rules_handler.static_validation(auth_rules_request)


def test_auth_rule_dynamic_validation_without_permission(auth_rules_request,
                                                         auth_rules_handler: AuthRulesHandler, creator):
    add_to_idr(auth_rules_handler.database_manager.idr_cache, creator, STEWARD)
    with pytest.raises(UnauthorizedClientRequest):
        auth_rules_handler.dynamic_validation(auth_rules_request, 0)


def test_auth_rule_dynamic_validation(auth_rules_request,
                                      auth_rules_handler: AuthRulesHandler, creator):
    add_to_idr(auth_rules_handler.database_manager.idr_cache, creator, TRUSTEE)


def test_update_state(auth_rules_request, auth_rules_handler: AuthRulesHandler):
    txn = reqToTxn(auth_rules_request)
    payload = get_payload_data(txn)
    for rule in payload[RULES]:
        constraint = StaticAuthRuleHelper.get_auth_constraint(rule)
        auth_key = StaticAuthRuleHelper.get_auth_key(rule)
        path = AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key)

        auth_rules_handler.update_state(txn, None, auth_rules_request)
        assert auth_rules_handler.get_from_state(path) == constraint.as_dict
