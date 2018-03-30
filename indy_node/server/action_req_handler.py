from typing import List

import dateutil.parser

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, isTxnForced
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE, DATA
from indy_common.auth import Authoriser
from indy_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, \
    POOL_CONFIG, NODE_UPGRADE, POOL_RESTART
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.restarter import Restarter
from indy_node.server.pool_config import PoolConfig


class ActionReqHandler(RequestHandler):
    action_types = {POOL_RESTART}

    def __init__(self, idrCache: IdrCache,
                 restarter: Restarter, poolManager, poolCfg: PoolConfig):
        self.idrCache = idrCache
        self.restarter = restarter
        self.poolManager = poolManager
        self.poolCfg = poolCfg

    def doStaticValidation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        if operation[TXN_TYPE] == POOL_RESTART:
            self._doStaticValidationPoolRestart(identifier, req_id, operation)

    def _doStaticValidationPoolRestart(self, identifier, req_id, operation):
        if SCHEDULE in operation.keys() is None and operation[SCHEDULE] != "0":
            try:
                dateutil.parser.parse(operation[SCHEDULE])
            except Exception:
                raise InvalidClientRequest(identifier, req_id,
                                           "time is not valid")

    def validate(self, req: Request):
        status = None
        operation = req.operation
        typ = operation.get(TXN_TYPE)
        if typ not in [POOL_RESTART]:
            return
        origin = req.identifier
        try:
            originRole = self.idrCache.getRole(origin, isCommitted=False)
        except BaseException:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "Nym {} not added to the ledger yet".format(origin))
        action = ""
        if typ == POOL_RESTART:
            action = operation.get(ACTION)
        r, msg = Authoriser.authorised(
            typ, originRole, field=ACTION, oldVal=status, newVal=action)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier, req.reqId, "{} cannot do restart".format(
                    Roles.nameFromValue(originRole)))

    def applyRestart(self, req: Request):
        txn = reqToTxn(req)
        self.restarter.handleActionTxn(txn)
        self.poolCfg.handleConfigTxn(txn)
