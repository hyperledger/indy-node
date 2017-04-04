from plenum.common.exceptions import InvalidClientRequest
from plenum.server.req_handler import ReqHandler as PHandler
from sovrin_common.constants import \
    POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, TXN_TYPE


class ConfigReqHandler(PHandler):
    def __init__(self, ledger, state):
        self.ledger = ledger
        self.state = state

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
