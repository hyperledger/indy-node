from typing import List

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE
from sovrin_common.auth import Authoriser
from sovrin_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, POOL_CONFIG
from sovrin_common.roles import Roles
from sovrin_common.transactions import SovrinTransactions
from sovrin_common.types import Request
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.upgrader import Upgrader
from sovrin_node.server.pool_config import PoolConfig


class ConfigReqHandler(RequestHandler):
    def __init__(self, ledger, state, idrCache: IdrCache, upgrader: Upgrader, poolManager, poolCfg: PoolConfig):
        super().__init__(ledger, state)
        self.idrCache = idrCache
        self.upgrader = upgrader
        self.poolManager = poolManager
        self.poolCfg = poolCfg

    def doStaticValidation(self, identifier, reqId, operation):
        if operation[TXN_TYPE] == POOL_UPGRADE:
            self._doStaticValidationPoolUpgrade(identifier, reqId, operation)
        elif operation[TXN_TYPE] == POOL_CONFIG:
            self._doStaticValidationPoolConfig(identifier, reqId, operation)

    def _doStaticValidationPoolConfig(self, identifier, reqId, operation):
        pass

    def _doStaticValidationPoolUpgrade(self, identifier, reqId, operation):
        action = operation.get(ACTION)
        if action not in (START, CANCEL):
            raise InvalidClientRequest(identifier, reqId,
                                       "{} not a valid action".
                                       format(action))
        if action == START:
            schedule = operation.get(SCHEDULE, {})
            force = operation.get(FORCE)
            force = str(force) == 'True'
            isValid, msg = self.upgrader.isScheduleValid(schedule,
                                                         self.poolManager.nodeIds,
                                                         force)
            if not isValid:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid schedule since {}".
                                           format(schedule, msg))

        # TODO: Check if cancel is submitted before start

    def validate(self, req: Request, config=None):
        operation = req.operation
        typ = operation.get(TXN_TYPE)
        if typ not in [POOL_UPGRADE, POOL_CONFIG]:
            return
        origin = req.identifier
        try:
            originRole = self.idrCache.getRole(origin, isCommitted=False)
        except:
            raise UnauthorizedClientRequest(req.identifier, req.reqId,
                                            "Nym {} not added to the ledger yet".format(origin))
        if typ == POOL_UPGRADE:
            trname = SovrinTransactions.POOL_UPGRADE.name
            action = operation.get(ACTION)
            # TODO: Some validation needed for making sure name and version
            # present
            status = self.upgrader.statusInLedger(req.operation.get(NAME), req.operation.get(VERSION))
            if status == START and action == START:
                raise InvalidClientRequest(req.identifier, req.reqId,
                                           "Upgrade '{}' is already scheduled".format(req.operation.get(NAME)))
        elif typ == POOL_CONFIG:
            trname = SovrinTransactions.POOL_CONFIG.name
            action = None
            status = None

        r, msg = Authoriser.authorised(typ, ACTION, originRole, oldVal=status, newVal=action)
        if not r:
            raise UnauthorizedClientRequest(req.identifier, req.reqId,
                                            "{} cannot do {}".format(Roles.nameFromValue(originRole), trname))

    def apply(self, req: Request, cons_time):
        txn = reqToTxn(req, cons_time)
        self.ledger.appendTxns([txn])
        return txn

    def commit(self, txnCount, stateRoot, txnRoot) -> List:
        committedTxns = super().commit(txnCount, stateRoot, txnRoot)
        for txn in committedTxns:
            # TODO: for now pool_upgrade will not be scheduled twice
            # because of version check
            # make sure it will be the same in future
            self.upgrader.handleUpgradeTxn(txn)
            self.poolCfg.handleConfigTxn(txn)
        return committedTxns

    def applyForced(self, req: Request):
        if req.isForced():
            txn = reqToTxn(req)
            self.upgrader.handleUpgradeTxn(txn)
            self.poolCfg.handleConfigTxn(txn)
