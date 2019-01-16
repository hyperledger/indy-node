from indy_node.server.request_handlers.action_req_handlers.utils import generate_action_result
from indy_node.server.restarter import Restarter

from indy_common.constants import POOL_RESTART

from plenum.common.request import Request
from plenum.common.txn_util import get_request_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.action_request_handler import ActionRequestHandler
from stp_core.common.log import getlogger

logger = getlogger()


class PoolRestartHandler(ActionRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 restarter: Restarter):
        super().__init__(database_manager, POOL_RESTART, None)
        self.restarter = restarter

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)

        logger.debug("Transaction {} with type {} started"
                     .format(req_id, request.txn_type))
        self.restarter.handleRestartRequest(request)
        result = generate_action_result(request)
        logger.debug("Transaction {} with type {} finished"
                     .format(req_id, request.txn_type))
        return result

    def process_action(self, request: Request):
        self._validate_request_type(request)
