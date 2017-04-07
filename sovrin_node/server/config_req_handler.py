from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION
from sovrin_common.auth import Authoriser
from sovrin_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION
from sovrin_common.types import Request
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.upgrader import Upgrader


class ConfigReqHandler(RequestHandler):
    def __init__(self, ledger, state, idrCache: IdrCache, upgrader: Upgrader,
                 poolManager):
        super().__init__(ledger, state)
        self.idrCache = idrCache
        self.upgrader = upgrader
        self.poolManager = poolManager

    def validate(self, req: Request, config=None):
        origin = req.identifier
        try:
            originRole = self.idrCache.getRole(origin, isCommitted=False)
        except:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "Nym {} not added to the ledger yet".format(origin))

        action = req.operation.get(ACTION)
        # TODO: Some validation needed for making sure name and version
        # present
        status = self.upgrader.statusInLedger(req.operation.get(NAME),
                                              req.operation.get(VERSION))

        r, msg = Authoriser.authorised(POOL_UPGRADE, ACTION, originRole,
                                       oldVal=status, newVal=action)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "{} cannot do {}".format(originRole, POOL_UPGRADE))

    def doStaticValidation(self, identifier, reqId, operation):
        if operation[TXN_TYPE] == POOL_UPGRADE:
            action = operation.get(ACTION)
            if action not in (START, CANCEL):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid action".
                                           format(action))
            if action == START:
                schedule = operation.get(SCHEDULE, {})
                isValid, msg = self.upgrader.isScheduleValid(schedule,
                                                             self.poolManager.nodeIds)
                if not isValid:
                    raise InvalidClientRequest(identifier, reqId,
                                               "{} not a valid schedule since {}".
                                               format(schedule, msg))

            # TODO: Check if cancel is submitted before start
