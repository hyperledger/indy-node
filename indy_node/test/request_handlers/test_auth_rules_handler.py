import pytest
from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_map import auth_map

from indy_common.constants import OLD_VALUE, AUTH_TYPE, ROLE, ENDORSER, AUTH_ACTION, \
    AUTH_RULES, RULES

from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler import AuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rules_handler import AuthRulesHandler
from indy_node.test.auth_rule.helper import generate_auth_rule_operation, generate_auth_rule
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from plenum.common.constants import TRUSTEE, TXN_TYPE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def auth_rule_handler(db_manager):
    f = FakeSomething()
    f.validate = lambda request, action_list: True
    f.auth_map = auth_map
    return AuthRulesHandler(db_manager, f)


@pytest.fixture(scope="function")
def auth_rule_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={TXN_TYPE: AUTH_RULES,
                              RULES: [generate_auth_rule()]})


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier


def test_auth_rule_static_validation(auth_rule_request, auth_rule_handler: AuthRuleHandler):
    auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_static_validation_failed_without_old_value(auth_rule_request,
                                                              auth_rule_handler: AuthRuleHandler):
    rule = auth_rule_request.operation[RULES][0]
    if OLD_VALUE in rule:
        del rule[OLD_VALUE]
    rule[AUTH_ACTION] = EDIT_PREFIX
    with pytest.raises(InvalidClientRequest, match="EDIT must contain field old_value"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_static_validation_failed_with_excess_field(auth_rule_request,
                                                              auth_rule_handler: AuthRuleHandler):
    rule = auth_rule_request.operation[RULES][0]
    rule[OLD_VALUE] = "old_value"
    rule[AUTH_TYPE] = ADD_PREFIX
    with pytest.raises(InvalidClientRequest, match="ADD must not contain field old_value"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_static_validation_failed_with_incorrect_key(auth_rule_request,
                                                               auth_rule_handler: AuthRuleHandler):
    auth_rule_request.operation[RULES].append(generate_auth_rule(auth_action=ADD_PREFIX,
                                                                 auth_type="wrong_type",
                                                                 field=ROLE, new_value=ENDORSER))
    with pytest.raises(InvalidClientRequest, match="key .* is not found in authorization map"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_dynamic_validation(auth_rule_request,
                                      auth_rule_handler: AuthRuleHandler, creator):
    auth_rule_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(auth_rule_handler.database_manager.idr_cache, creator, TRUSTEE)
    auth_rule_handler.dynamic_validation(auth_rule_request)

    auth_rule_handler.write_req_validator.validate = get_exception(True)
    with pytest.raises(UnauthorizedClientRequest):
        auth_rule_handler.dynamic_validation(auth_rule_request)
