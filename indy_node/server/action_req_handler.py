from typing import List

from indy_node.server.restarter import Restarter
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, isTxnForced
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE, DATA
from indy_common.auth import Authoriser
from indy_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, POOL_CONFIG, NODE_UPGRADE, POOL_RESTART
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.upgrader import Upgrader
from indy_node.server.pool_config import PoolConfig


class ConfigReqHandler(RequestHandler):
    action_types = {POOL_RESTART}

    def __init__(self, ledger, state, idrCache: IdrCache,
                 upgrader: Upgrader, restarter: Restarter, poolManager, poolCfg: PoolConfig):
        super().__init__(ledger, state)
        self.idrCache = idrCache
        self.upgrader = upgrader
        self.restarter = restarter
        self.poolManager = poolManager
        self.poolCfg = poolCfg

    def doStaticValidation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        if operation[TXN_TYPE] == POOL_RESTART:
            self._doStaticValidationPoolRestart(identifier, req_id, operation)

    def _doStaticValidationPoolRestart(self, identifier, req_id, operation):
        if not operation.get(DATA).get(SCHEDULE):
            raise InvalidClientRequest(identifier, req_id,
                                       "time for restart can not be empty")

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
        if typ == POOL_RESTART:
            action = operation.get(ACTION)
        r, msg = Authoriser.authorised(
            typ, originRole, field=ACTION, oldVal=status, newVal=action)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier, req.reqId, "{} cannot do {}".format(
                    Roles.nameFromValue(originRole), trname))

    def apply(self, req: Request, cons_time):
        txn = reqToTxn(req, cons_time)
        (start, _), _ = self.ledger.appendTxns([txn])
        return start, txn

    def commit(self, txnCount, stateRoot, txnRoot, ppTime) -> List:
        committedTxns = super().commit(txnCount, stateRoot, txnRoot, ppTime)
        for txn in committedTxns:
            # Handle POOL_UPGRADE or POOL_CONFIG transaction here
            # only in case it is not forced.
            # If it is forced then it was handled earlier
            # in applyForced method.
            if not isTxnForced(txn):
                self.upgrader.handleUpgradeTxn(txn)
                self.poolCfg.handleConfigTxn(txn)
        return committedTxns

    def applyRestart(self, req: Request):
            txn = reqToTxn(req)
            self.restarter.handleRestartTxn(txn)
            self.poolCfg.handleConfigTxn(txn)
