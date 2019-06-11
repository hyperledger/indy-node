from common.serializers.serialization import state_roots_serializer, domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.state import config
from indy_common.types import ClientGetAuthRuleOperation
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from plenum.common.txn_util import get_request_data
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler

from indy_common.authorize.auth_actions import EDIT_PREFIX, split_action_id
from indy_common.constants import CONFIG_LEDGER_ID, AUTH_ACTION, OLD_VALUE, \
    NEW_VALUE, AUTH_TYPE, FIELD, CONSTRAINT, GET_AUTH_RULE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class GetAuthRuleHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        self.write_req_validator = write_req_validator
        self.constraint_serializer = ConstraintsSerializer(domain_state_serializer)
        super().__init__(database_manager, GET_AUTH_RULE, CONFIG_LEDGER_ID)

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        required_fields = list(dict(ClientGetAuthRuleOperation.schema).keys())
        required_fields.remove(OLD_VALUE)
        if len(operation) > 1:
            if not set(required_fields).issubset(set(operation.keys())):
                raise InvalidClientRequest(identifier, req_id,
                                           "Not enough fields to build an auth key.")
            StaticAuthRuleHelper.check_auth_key(operation, identifier, req_id, self.write_req_validator.auth_map)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        operation = request.operation
        proof = None
        if len(operation) >= len(ClientGetAuthRuleOperation.schema) - 1:
            path = StaticAuthRuleHelper.get_auth_key(operation)
            data, proof = self._get_auth_rule(path)
        else:
            data = self._get_all_auth_rules()
        result = self.make_result(request=request,
                                  data=data,
                                  proof=proof)
        result.update(operation)
        return result

    def _get_auth_rule(self, key):
        path = config.make_state_path_for_auth_rule(key)
        map_data, proof = self._get_value_from_state(path, with_proof=True)

        if map_data:
            data = self.constraint_serializer.deserialize(map_data)
        else:
            data = self.write_req_validator.auth_map[key]
        action_obj = split_action_id(key)
        return [self.make_auth_rule_data(data, action_obj)], proof

    def _get_all_auth_rules(self):
        data = self.write_req_validator.auth_map.copy()
        result = []
        for key in self.write_req_validator.auth_map:
            path = AbstractAuthRuleHandler.make_state_path_for_auth_rule(key)
            state_constraint, _ = self._get_value_from_state(path)
            if state_constraint:
                value = self.constraint_serializer.deserialize(state_constraint)
            else:
                value = data[key]
            action_obj = split_action_id(key)
            result.append(self.make_auth_rule_data(value, action_obj))
        return result

    @staticmethod
    def make_auth_rule_data(constraint, action_obj):
        result = {CONSTRAINT: constraint.as_dict if constraint is not None else {},
                  AUTH_TYPE: action_obj.txn_type,
                  AUTH_ACTION: action_obj.prefix,
                  FIELD: action_obj.field,
                  NEW_VALUE: action_obj.new_value,
                  }
        if action_obj.prefix == EDIT_PREFIX:
            result[OLD_VALUE] = action_obj.old_value
        return result
