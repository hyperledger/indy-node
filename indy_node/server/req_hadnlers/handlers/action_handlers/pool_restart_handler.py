from indy_common.roles import Roles

from plenum.common.exceptions import UnauthorizedClientRequest

from common.exceptions import LogicError
from indy_common.constants import POOL_RESTART, ACTION
from indy_common.auth import Authoriser

from plenum.common.request import Request
from plenum.common.constants import TXN_TYPE

from plenum.server.req_handlers.handler_interfaces.action_handler import ActionHandler


class PoolRestartHandler(ActionHandler):
    operation_type = POOL_RESTART

    def __init__(self, idr_cache):
        self.idr_cache = idr_cache

    def validate(self, request: Request):
        operation = request.operation
        request_type = operation.get(TXN_TYPE)
        if self.operation_type != request_type:
            # TODO: In previous implementation we just make return, probably we need to raise logic error?
            raise LogicError("PoolRestartHandler can validate only POOL_RESTART ({}) request. "
                             "Got {} instead".format(self.operation_type, request_type))

        action = operation.get(ACTION)
        identifier = request.identifier
        req_id = request.reqId
        try:
            origin_role = self.idr_cache.getRole(identifier, isCommitted=False)
        except BaseException:
            raise UnauthorizedClientRequest(
                identifier,
                req_id,
                "Nym {} not added to the ledger yet".format(identifier))

        r, msg = Authoriser.authorised(request_type,
                                       origin_role,
                                       field=ACTION,
                                       oldVal=None,
                                       newVal=action)
        if not r:
            raise UnauthorizedClientRequest(
                identifier, req_id,
                "{} cannot do action with type = {}".format(
                    Roles.nameFromValue(origin_role),
                    request_type))

    def execute(self, identifier, req_id, operation):
        pass
