from abc import abstractmethod

from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from plenum.common.exceptions import InvalidClientRequest
from indy_common.config_util import getConfig
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class AbstractRichSchemaReadRequestHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager, txn_type, ledger_id):
        super().__init__(database_manager, txn_type, ledger_id)
        self.config = getConfig()

    def _enabled(self) -> bool:
        return self.config.ENABLE_RICH_SCHEMAS

    def _validate_enabled(self, request: Request):
        if not self._enabled():
            raise InvalidClientRequest(request.identifier, request.reqId, "RichSchema queries are disabled")

    @abstractmethod
    def get_result(self, request: Request):
        super().get_result(request)
        self._validate_enabled(request)
