from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler

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


class GetAuthRuleHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, AUTH_RULE, CONFIG_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        data, seq_no, update_time, proof = self._get_auth_map()
        result = self.make_result(request=request,
                                  data=data,
                                  last_seq_no=seq_no,
                                  update_time=update_time,
                                  proof=proof)

        result.update(request.operation)
        return result

    def _get_auth_map(self):
        data, seq_no, update_time, proof = None, None, None, None
        return data, seq_no, update_time, proof
