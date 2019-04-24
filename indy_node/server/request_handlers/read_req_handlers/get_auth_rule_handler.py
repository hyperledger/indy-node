from indy_common.types import ClientGetAuthRuleOperation
from plenum.common.txn_util import get_request_data
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler

from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, AuthActionAdd
from indy_common.constants import CONFIG_LEDGER_ID, AUTH_RULE, AUTH_ACTION, OLD_VALUE, \
    NEW_VALUE, AUTH_TYPE, FIELD
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class GetAuthRuleHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        self.write_req_validator = None  # TODO: add filling write_req_validator
        super().__init__(database_manager, AUTH_RULE, CONFIG_LEDGER_ID)

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        required_fields = list(dict(ClientGetAuthRuleOperation.schema).keys())
        required_fields.remove(OLD_VALUE)
        if len(operation) > 1:
            if not set(required_fields).issubset(set(operation.keys())):
                raise InvalidClientRequest(identifier, req_id,
                                           "Not enough fields to build an auth key.")
            self._check_auth_key(operation, identifier, req_id)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        operation = request.operation
        proof = None
        if len(operation) >= len(ClientGetAuthRuleOperation.schema) - 1:
            path = self.get_auth_key(operation)
            data, proof = self._get_auth_rule(path)
        else:
            data = self._get_all_auth_rules()
        result = self.make_result(request=request,
                                  data=data,
                                  proof=proof)
        result.update(operation)
        return result

    def _get_auth_rule(self, path):
        proof = None
        try:
            data, last_seq_no, last_update_time, proof = self.lookup(path, is_committed=True, with_proof=True)
        except KeyError:
            data = self.write_req_validator.auth_map[path]
        return {path: data.as_dict}, proof

    def _get_all_auth_rules(self):
        data = {}
        for key in self.write_req_validator.auth_map:
            try:
                state_constraint, _, _, proof = self.lookup(key, is_committed=True, with_proof=True)
                data[key] = state_constraint.as_dict
            except KeyError:
                data[key] = self.write_req_validator.auth_map[key].as_dict
        return data

    def _check_auth_key(self, operation, identifier, req_id):
        auth_key = self.get_auth_key(operation)

        if auth_key not in self.write_req_validator.auth_map and \
                auth_key not in self.write_req_validator.anyone_can_write_map:
            raise InvalidClientRequest(identifier, req_id,
                                       "Unknown authorization rule: key '{}' is not "
                                       "found in authorization map.".format(auth_key))

    @staticmethod
    def get_auth_key(operation):
        action = operation.get(AUTH_ACTION, None)
        old_value = operation.get(OLD_VALUE, None)
        new_value = operation.get(NEW_VALUE, None)
        auth_type = operation.get(AUTH_TYPE, None)
        field = operation.get(FIELD, None)

        return AuthActionEdit(txn_type=auth_type,
                              field=field,
                              old_value=old_value,
                              new_value=new_value).get_action_id() \
            if action == EDIT_PREFIX else \
            AuthActionAdd(txn_type=auth_type,
                          field=field,
                          value=new_value).get_action_id()
