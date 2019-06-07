from indy_node.server.pool_config import PoolConfig

from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import POOL_CONFIG, CONFIG_LEDGER_ID, ACTION
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class PoolConfigHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator,
                 pool_config: PoolConfig):
        super().__init__(database_manager, POOL_CONFIG, CONFIG_LEDGER_ID)
        self.write_req_validator = write_req_validator
        self.pool_config = pool_config

    def static_validation(self, request: Request):
        self._validate_request_type(request)

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        action = '*'
        status = '*'
        self.write_req_validator.validate(request,
                                          [AuthActionEdit(txn_type=self.txn_type,
                                                          field=ACTION,
                                                          old_value=status,
                                                          new_value=action)])

    def apply_forced_request(self, req: Request):
        super().apply_forced_request(req)
        txn = self._req_to_txn(req)
        self.pool_config.handleConfigTxn(txn)

    # Config handler don't use state for any validation for now
    def update_state(self, txn, prev_result, request, is_committed=False):
        pass
