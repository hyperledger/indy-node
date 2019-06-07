from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import VALIDATOR_INFO
from indy_node.server.request_handlers.action_req_handlers.utils import generate_action_result
from plenum.common.constants import DATA
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data
from plenum.server.database_manager import DatabaseManager

from plenum.server.request_handlers.handler_interfaces.action_request_handler import ActionRequestHandler
from stp_core.common.log import getlogger

logger = getlogger()


class ValidatorInfoHandler(ActionRequestHandler):
    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator,
                 info_tool):
        super().__init__(database_manager, VALIDATOR_INFO, None)
        self.write_req_validator = write_req_validator
        self.info_tool = info_tool

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        self.write_req_validator.validate(request,
                                          [AuthActionAdd(txn_type=VALIDATOR_INFO,
                                                         field='*',
                                                         value='*')])

    def process_action(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        logger.debug("Transaction {} with type {} started"
                     .format(req_id, request.txn_type))
        result = generate_action_result(request)
        result[DATA] = self.info_tool.info
        result[DATA].update(self.info_tool.memory_profiler)
        result[DATA].update(self.info_tool._generate_software_info())
        result[DATA].update(self.info_tool.extractions)
        result[DATA].update(self.info_tool.node_disk_size)
        logger.debug("Transaction {} with type {} finished"
                     .format(req_id, request.txn_type))
        return result
