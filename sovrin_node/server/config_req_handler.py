from plenum.common.exceptions import InvalidClientRequest
from plenum.server.req_handler import RequestHandler
from plenum.common.constants import TXN_TYPE
from sovrin_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION


class ConfigReqHandler(RequestHandler):

    def __init__(self, ledger, state):
        super().__init__(ledger, state)

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
