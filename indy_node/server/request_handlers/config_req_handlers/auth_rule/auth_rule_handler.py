from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import AUTH_RULE
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data
from plenum.server.database_manager import DatabaseManager


class AuthRuleHandler(AbstractAuthRuleHandler):

    def __init__(self, database_manager: DatabaseManager, write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, write_req_validator, AUTH_RULE)

    def static_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        self._validate_request_type(request)
        self._static_validation_for_rule(operation, identifier, req_id)

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        self.write_req_validator.validate(request,
                                          [AuthActionEdit(txn_type=AUTH_RULE,
                                                          field="*",
                                                          old_value="*",
                                                          new_value="*")])

    def update_state(self, txn, prev_result, request=None, is_committed=False):
        payload = get_payload_data(txn)
        constraint = StaticAuthRuleHelper.get_auth_constraint(payload)
        auth_key = StaticAuthRuleHelper.get_auth_key(payload)
        self._update_auth_constraint(auth_key, constraint)
