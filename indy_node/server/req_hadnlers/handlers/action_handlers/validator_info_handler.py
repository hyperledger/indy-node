from indy_common.roles import Roles

from indy_common.auth import Authoriser

from plenum.common.exceptions import UnauthorizedClientRequest

from common.exceptions import LogicError

from plenum.common.constants import TXN_TYPE

from indy_common.constants import VALIDATOR_INFO, ACTION

from plenum.common.request import Request

from plenum.server.req_handlers.handler_interfaces.action_handler import ActionHandler


class ValidatorInfoHandler(ActionHandler):
    operation_type = VALIDATOR_INFO

    def __init__(self, idr_cache):
        self.idr_cache = idr_cache

    def validate(self, request: Request):
        operation = request.operation
        request_type = operation.get(TXN_TYPE)
        if self.operation_type != request_type:
            # TODO: In previous implementation we just make return, probably we need to raise logic error?
            raise LogicError("ValidatorInfoHandler can validate only ValidatorInfo ({}) request. "
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
