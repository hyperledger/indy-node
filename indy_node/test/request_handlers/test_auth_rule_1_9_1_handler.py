import pytest
from indy_common.authorize.auth_constraints import OFF_LEDGER_SIGNATURE
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler import AuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler_1_9_1 import AuthRuleHandler191
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.txn_util import reqToTxn, get_payload_data


@pytest.fixture(scope="module")
def auth_rule_handler_1_9_1(db_manager, write_auth_req_validator):
    return AuthRuleHandler191(db_manager, write_auth_req_validator)


def test_update_state(auth_rule_request, auth_rule_handler_1_9_1: AuthRuleHandler):
    txn = reqToTxn(auth_rule_request)
    payload = get_payload_data(txn)
    constraint = StaticAuthRuleHelper.get_auth_constraint(payload)
    auth_key = StaticAuthRuleHelper.get_auth_key(payload)
    path = AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key)

    auth_rule_handler_1_9_1.update_state(txn, None, auth_rule_request)
    expected_dict = constraint.as_dict
    expected_dict[OFF_LEDGER_SIGNATURE] = False
    assert auth_rule_handler_1_9_1.get_from_state(path) == expected_dict

