from typing import Optional

from plenum.common.exceptions import InvalidClientRequest
from indy_common.constants import NODE_UPGRADE, CONFIG_LEDGER_ID
from indy_common.types import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class NodeUpgradeHandler(WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super(NodeUpgradeHandler, self).__init__(database_manager=database_manager,
                                                 txn_type=NODE_UPGRADE,
                                                 ledger_id=CONFIG_LEDGER_ID)

    def update_state(self, txn, prev_result, request, is_committed=False):
        pass

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        pass

    def static_validation(self, request: Request):
        raise InvalidClientRequest(request.identifier, request.reqId,
                                   "External NODE_UPGRADE requests are not allowed")
