import pytest
from indy_common.auth import Authoriser
from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraintOr
from indy_common.authorize.auth_map import auth_map

from indy_common.constants import NYM, AUTH_RULE, OLD_VALUE, AUTH_TYPE, ROLE, ENDORSER, CONSTRAINT, AUTH_ACTION
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler

from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler import AuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from indy_common.test.auth.conftest import write_auth_req_validator
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething
from indy_common.test.auth.conftest import write_auth_req_validator, constraint_serializer, config_state


@pytest.fixture(scope="module")
def auth_rule_handler(db_manager, write_auth_req_validator):
    return AuthRuleHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def auth_rule_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   signature="sig",
                   operation=generate_auth_rule_operation())


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
    if OLD_VALUE in auth_rule_request.operation:
        del auth_rule_request.operation[OLD_VALUE]
    auth_rule_request.operation[AUTH_ACTION] = EDIT_PREFIX
    with pytest.raises(InvalidClientRequest, match="EDIT must contain field old_value"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_static_validation_failed_with_excess_field(auth_rule_request,
                                                              auth_rule_handler: AuthRuleHandler):
    auth_rule_request.operation[OLD_VALUE] = "old_value"
    auth_rule_request.operation[AUTH_TYPE] = ADD_PREFIX
    with pytest.raises(InvalidClientRequest, match="ADD must not contain field old_value"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_static_validation_failed_with_incorrect_key(auth_rule_request,
                                                               auth_rule_handler: AuthRuleHandler):
    auth_rule_request.operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                               auth_type="wrong_type",
                                                               field=ROLE, new_value=ENDORSER)
    with pytest.raises(InvalidClientRequest, match="key .* is not found in authorization map"):
        auth_rule_handler.static_validation(auth_rule_request)


def test_auth_rule_dynamic_validation_without_permission(auth_rule_request,
                                                         auth_rule_handler: AuthRuleHandler, creator):
    add_to_idr(auth_rule_handler.database_manager.idr_cache, creator, STEWARD)
    with pytest.raises(UnauthorizedClientRequest):
        auth_rule_handler.dynamic_validation(auth_rule_request)


def test_auth_rule_dynamic_validation(auth_rule_request,
                                      auth_rule_handler: AuthRuleHandler, creator):
    add_to_idr(auth_rule_handler.database_manager.idr_cache, creator, TRUSTEE)
    auth_rule_handler.dynamic_validation(auth_rule_request)


def test_update_state(auth_rule_request, auth_rule_handler: AuthRuleHandler):
    txn = reqToTxn(auth_rule_request)
    payload = get_payload_data(txn)
    constraint = StaticAuthRuleHelper.get_auth_constraint(payload)
    auth_key = StaticAuthRuleHelper.get_auth_key(payload)
    path = AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key)

    auth_rule_handler.update_state(txn, None, auth_rule_request)
    assert auth_rule_handler.get_from_state(path) == constraint.as_dict

