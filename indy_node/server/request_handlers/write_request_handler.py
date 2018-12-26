from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import \
    WriteRequestHandler as PWriteRequestHandler


class WriteRequestHandler(PWriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager, txn_type, ledger_id,
                 write_request_validator: WriteRequestValidator):
        super().__init__(database_manager, txn_type, ledger_id)
        self.write_request_validator = write_request_validator
