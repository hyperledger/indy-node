from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintCreator, ConstraintsSerializer

from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import CONFIG_LEDGER_ID, AUTH_RULE, CONSTRAINT, AUTH_ACTION, OLD_VALUE, \
    NEW_VALUE, AUTH_TYPE, FIELD
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class AuthRuleHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, AUTH_RULE, CONFIG_LEDGER_ID)
        self.write_req_validator = write_req_validator
        self.constraint_serializer = ConstraintsSerializer(domain_state_serializer)

    def static_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        self._validate_request_type(request)
        constraint = operation.get(CONSTRAINT)
        ConstraintCreator.create_constraint(constraint)

        action = operation.get(AUTH_ACTION)
        old_value = operation.get(OLD_VALUE, None)
        new_value = operation.get(NEW_VALUE, None)
        auth_type = operation.get(AUTH_TYPE, None)
        field = operation.get(FIELD, None)
        if old_value is None and action == EDIT_PREFIX:
            raise InvalidClientRequest(identifier, req_id,
                                       "Transaction for change authentication "
                                       "rules for {}={} must contain field {}".
                                       format(AUTH_ACTION, EDIT_PREFIX, OLD_VALUE))
        auth_key = AuthActionEdit(txn_type=auth_type,
                                  field=field,
                                  old_value=old_value,
                                  new_value=new_value).get_action_id() \
            if action == EDIT_PREFIX else \
            AuthActionAdd(txn_type=auth_type,
                          field=field,
                          value=new_value).get_action_id()
        if auth_key not in self.write_req_validator.auth_map:
            raise InvalidClientRequest(identifier, req_id,
                                       "Key '{}' is not contained in the "
                                       "authorization map".format(auth_key))

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        self.write_req_validator.validate(request,
                                          [AuthActionEdit(txn_type=AUTH_RULE,
                                                          field="*",
                                                          old_value="*",
                                                          new_value="*")])

    @staticmethod
    def get_auth_constraint(txn):
        operation = get_payload_data(txn)
        return ConstraintCreator.create_constraint(operation.get(CONSTRAINT))

    def update_auth_constraint(self, auth_key, constraint):
        self.state.set(auth_key.encode(),
                       self.constraint_serializer.serialize(constraint))

    def gen_state_key(self, txn):
        operation = get_payload_data(txn)
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

    def update_state(self, txn, prev_result, is_committed=False):
        constraint = self.get_auth_constraint(txn)
        auth_key = self.gen_state_key(txn)
        self.update_auth_constraint(auth_key, constraint)
