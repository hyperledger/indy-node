from indy_common.authorize.auth_constraints import ConstraintCreator
from indy_node.server.pool_config import PoolConfig

from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import POOL_CONFIG, CONFIG_LEDGER_ID, ACTION, AUTH_RULE, CONSTRAINT, AUTH_ACTION, OLD_VALUE, \
    NEW_VALUE, AUTH_TYPE, FIELD
from indy_node.server.request_handlers.config_req_handlers.config_write_request_handler import ConfigWriteRequestHandler
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class AuthRuleHandler(ConfigWriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_request_validator: WriteRequestValidator):
        super().__init__(database_manager, AUTH_RULE, CONFIG_LEDGER_ID)
        self.write_request_validator = write_request_validator

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

    # Config handler don't use state for any validation for now
    def update_state(self, txn, prev_result, is_committed=False):
        pass

    def gen_state_key(self, txn):
        pass
