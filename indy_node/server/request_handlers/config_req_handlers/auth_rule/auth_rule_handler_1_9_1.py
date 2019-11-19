from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, ConstraintsEnum, OFF_LEDGER_SIGNATURE, \
    AUTH_CONSTRAINTS
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import AUTH_RULE
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler import AuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data
from plenum.server.database_manager import DatabaseManager


class AuthRuleHandler191(AuthRuleHandler):

    def _update_auth_constraint(self, auth_key: str, constraint):
        constraint_dict = constraint.as_dict if constraint else {}
        self._set_off_ledger_to_constraint(constraint_dict)
        self.state.set(AbstractAuthRuleHandler.make_state_path_for_auth_rule(auth_key),
                       self.constraint_serializer.serializer.serialize(constraint_dict))

    def _set_off_ledger_to_constraint(self, constraint_dict):
        if constraint_dict[CONSTRAINT_ID] == ConstraintsEnum.ROLE_CONSTRAINT_ID and \
                not constraint_dict.get(OFF_LEDGER_SIGNATURE, False):
            constraint_dict[OFF_LEDGER_SIGNATURE] = False
        for constraint in constraint_dict.get(AUTH_CONSTRAINTS, []):
            self._set_off_ledger_to_constraint(constraint)
