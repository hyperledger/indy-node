from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.types import f
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, DATA
from indy_common.constants import ACTION, POOL_RESTART, VALIDATOR_INFO
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.restarter import Restarter
from indy_node.server.pool_config import PoolConfig
from plenum.server.validator_info_tool import ValidatorNodeInfoTool
from stp_core.common.log import getlogger


logger = getlogger()


class ActionReqHandler(RequestHandler):
    operation_types = {POOL_RESTART, VALIDATOR_INFO}

    def __init__(self, idrCache: IdrCache,
                 restarter: Restarter, poolManager, poolCfg: PoolConfig,
                 info_tool: ValidatorNodeInfoTool, write_req_validator):
        self.idrCache = idrCache
        self.restarter = restarter
        self.info_tool = info_tool
        self.poolManager = poolManager
        self.poolCfg = poolCfg
        self.write_req_validator = write_req_validator

    def doStaticValidation(self, request: Request):
        pass

    def validate(self, req: Request):
        operation = req.operation
        typ = operation.get(TXN_TYPE)
        if typ not in self.operation_types:
            return
        if typ == POOL_RESTART:
            action = operation.get(ACTION)
            self.write_req_validator.validate(req,
                                              [AuthActionAdd(txn_type=POOL_RESTART,
                                                             field=ACTION,
                                                             value=action)])
        elif typ == VALIDATOR_INFO:
            self.write_req_validator.validate(req,
                                              [AuthActionAdd(txn_type=VALIDATOR_INFO,
                                                             field='*',
                                                             value='*')])

    def apply(self, req: Request, cons_time: int = None):
        logger.debug("Transaction {} with type {} started"
                     .format(req.reqId, req.txn_type))
        try:
            if req.txn_type == POOL_RESTART:
                self.restarter.handleRestartRequest(req)
                result = self._generate_action_result(req)
            elif req.txn_type == VALIDATOR_INFO:
                result = self._generate_action_result(req)
                result[DATA] = self.info_tool.info
                result[DATA].update(self.info_tool.memory_profiler)
                result[DATA].update(self.info_tool._generate_software_info())
                result[DATA].update(self.info_tool.extractions)
                result[DATA].update(self.info_tool.node_disk_size)
            else:
                raise InvalidClientRequest(
                    req.reqId,
                    "{} is not type of action transaction"
                    .format(req.txn_type))
        except Exception as ex:
            logger.warning("Operation is failed")
            raise ex
        logger.debug("Transaction {} with type {} finished"
                     .format(req.reqId, req.txn_type))
        return result

    def _generate_action_result(self, request: Request):
        return {**request.operation, **{
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId}}
