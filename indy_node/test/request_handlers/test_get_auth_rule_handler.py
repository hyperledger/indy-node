import pytest
from indy_common.auth import Authoriser
from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraintOr
from indy_common.authorize.auth_map import auth_map

from indy_common.constants import NYM, AUTH_RULE, OLD_VALUE, AUTH_TYPE, ROLE, ENDORSER, CONSTRAINT, AUTH_ACTION, \
    GET_AUTH_RULE

from indy_node.server.request_handlers.read_req_handlers.get_auth_rule_handler import GetAuthRuleHandler
from indy_node.test.auth_rule.helper import generate_auth_rule_operation, generate_key
from indy_common.test.auth.conftest import write_auth_req_validator
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from plenum.common.constants import STEWARD, TRUSTEE, TXN_TYPE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def get_auth_rule_handler(db_manager):
    f = FakeSomething()
    f.validate = lambda request, action_list: True
    f.auth_map = auth_map
    return GetAuthRuleHandler(db_manager, f)


@pytest.fixture(scope="function")
def get_auth_rule_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={TXN_TYPE: GET_AUTH_RULE,
                              **generate_key()})


@pytest.fixture(scope="function")
def get_all_auth_rules_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={TXN_TYPE: GET_AUTH_RULE})


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier


def test_auth_rule_static_validation(get_auth_rule_request, get_auth_rule_handler: GetAuthRuleHandler):
    get_auth_rule_handler.static_validation(get_auth_rule_request)


def test_all_auth_rules_static_validation(get_all_auth_rules_request, get_auth_rule_handler: GetAuthRuleHandler):
    get_auth_rule_handler.static_validation(get_all_auth_rules_request)


def test_auth_rule_static_validation_failed_without_old_value(get_auth_rule_request,
                                                              get_auth_rule_handler: GetAuthRuleHandler):
    if OLD_VALUE in get_auth_rule_request.operation:
        del get_auth_rule_request.operation[OLD_VALUE]
    get_auth_rule_request.operation[AUTH_ACTION] = EDIT_PREFIX
    with pytest.raises(InvalidClientRequest, match="EDIT must contain field old_value"):
        get_auth_rule_handler.static_validation(get_auth_rule_request)


def test_auth_rule_static_validation_failed_with_excess_field(get_auth_rule_request,
                                                              get_auth_rule_handler: GetAuthRuleHandler):
    get_auth_rule_request.operation[OLD_VALUE] = "old_value"
    get_auth_rule_request.operation[AUTH_ACTION] = ADD_PREFIX
    with pytest.raises(InvalidClientRequest, match="ADD must not contain field old_value"):
        get_auth_rule_handler.static_validation(get_auth_rule_request)


def test_auth_rule_static_validation_failed_with_incorrect_key(get_auth_rule_request,
                                                               get_auth_rule_handler: GetAuthRuleHandler):
    get_auth_rule_request.operation.update(generate_key(auth_action=EDIT_PREFIX,
                                                        auth_type="wrong_type",
                                                        field=ROLE,
                                                        new_value=ENDORSER,
                                                        old_value="*"))
    with pytest.raises(InvalidClientRequest, match="is not found in authorization map"):
        get_auth_rule_handler.static_validation(get_auth_rule_request)
