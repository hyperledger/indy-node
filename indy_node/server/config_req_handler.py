from typing import List

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, isTxnForced
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE
from indy_common.auth import Authoriser
from indy_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, POOL_CONFIG, NODE_UPGRADE
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.upgrader import Upgrader
from indy_node.server.pool_config import PoolConfig


class ConfigReqHandler(RequestHandler):
    write_types = {POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG}

    def __init__(self, ledger, state, idrCache: IdrCache,
                 upgrader: Upgrader, poolManager, poolCfg: PoolConfig):
        super().__init__(ledger, state)
        self.idrCache = idrCache
        self.upgrader = upgrader
        self.poolManager = poolManager
        self.poolCfg = poolCfg

    def doStaticValidation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        if operation[TXN_TYPE] == POOL_UPGRADE:
            self._doStaticValidationPoolUpgrade(identifier, req_id, operation)
        elif operation[TXN_TYPE] == POOL_CONFIG:
            self._doStaticValidationPoolConfig(identifier, req_id, operation)

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
            isValid, msg = self.upgrader.isScheduleValid(
                schedule, self.poolManager.getNodesServices(), force)
            if not isValid:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid schedule since {}".
                                           format(schedule, msg))

        # TODO: Check if cancel is submitted before start

    def validate(self, req: Request):
        status = None
        operation = req.operation
        typ = operation.get(TXN_TYPE)
        if typ not in [POOL_UPGRADE, POOL_CONFIG]:
            return
        origin = req.identifier
        try:
            originRole = self.idrCache.getRole(origin, isCommitted=False)
        except BaseException:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "Nym {} not added to the ledger yet".format(origin))
        if typ == POOL_UPGRADE:
            currentVersion = Upgrader.getVersion()
            targetVersion = req.operation[VERSION]
            if Upgrader.compareVersions(currentVersion, targetVersion) < 0:
                # currentVersion > targetVersion
                raise InvalidClientRequest(
                    req.identifier,
                    req.reqId,
                    "Upgrade to lower version is not allowed")

            trname = IndyTransactions.POOL_UPGRADE.name
            action = operation.get(ACTION)
            # TODO: Some validation needed for making sure name and version
            # present
            txn = self.upgrader.get_upgrade_txn(
                lambda txn: txn.get(
                    NAME,
                    None) == req.operation.get(
                    NAME,
                    None) and txn.get(VERSION) == req.operation.get(VERSION),
                reverse=True)
            if txn:
                status = txn.get(ACTION, None)

            if status == START and action == START:
                raise InvalidClientRequest(
                    req.identifier,
                    req.reqId,
                    "Upgrade '{}' is already scheduled".format(
                        req.operation.get(NAME)))
        elif typ == POOL_CONFIG:
            trname = IndyTransactions.POOL_CONFIG.name
            action = None
            status = None

        r, msg = Authoriser.authorised(
            typ, ACTION, originRole, oldVal=status, newVal=action)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier, req.reqId, "{} cannot do {}".format(
                    Roles.nameFromValue(originRole), trname))

    def apply(self, req: Request, cons_time):
        txn = reqToTxn(req, cons_time)
        (start, _), _ = self.ledger.appendTxns([txn])
        return start, txn

    def commit(self, txnCount, stateRoot, txnRoot) -> List:
        committedTxns = super().commit(txnCount, stateRoot, txnRoot)
        for txn in committedTxns:
            # Handle POOL_UPGRADE or POOL_CONFIG transaction here
            # only in case it is not forced.
            # If it is forced then it was handled earlier
            # in applyForced method.
            if not isTxnForced(txn):
                self.upgrader.handleUpgradeTxn(txn)
                self.poolCfg.handleConfigTxn(txn)
        return committedTxns

    def applyForced(self, req: Request):
        if req.isForced():
            txn = reqToTxn(req)
            self.upgrader.handleUpgradeTxn(txn)
            self.poolCfg.handleConfigTxn(txn)
