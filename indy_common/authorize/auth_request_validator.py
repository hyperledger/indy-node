from abc import abstractmethod

from indy_common.authorize.auth_cons_strategies import LocalAuthStrategy
from indy_common.authorize.auth_actions import AbstractAuthAction
from indy_common.authorize.auth_constraints import AND_CONSTRAINT_ID, OR_CONSTRAINT_ID, ROLE_CONSTRAINT_ID
from indy_common.authorize.authorizer import AbstractAuthorizer, CompositeAuthorizer, RolesAuthorizer, AndAuthorizer, \
    OrAuthorizer, AuthValidationError
from indy_common.types import Request
from plenum.common.exceptions import UnauthorizedClientRequest
from stp_core.common.log import getlogger


logger = getlogger()


class AbstractRequestValidator(AbstractAuthorizer):

    @abstractmethod
    def validate(self, request, action_list: [AbstractAuthAction]):
        raise NotImplementedError()


class WriteRequestValidator(AbstractRequestValidator, CompositeAuthorizer):
    def __init__(self, config, auth_map, cache):
        CompositeAuthorizer.__init__(self)
        self.cache = cache
        self.config = config
        self.auth_map = auth_map
        self.auth_cons_strategy = self.create_auth_strategy()
        self.register_default_authorizers()

    def register_default_authorizers(self):
        self.register_authorizer(RolesAuthorizer(cache=self.cache), auth_constraint_id=ROLE_CONSTRAINT_ID)
        self.register_authorizer(AndAuthorizer(), auth_constraint_id=AND_CONSTRAINT_ID)
        self.register_authorizer(OrAuthorizer(), auth_constraint_id=OR_CONSTRAINT_ID)

    def validate(self, request: Request, action_list: [AbstractAuthAction]):
        for action in action_list:
            action_id = action.get_action_id()
            auth_constraint = self.auth_cons_strategy.get_auth_constraint(action_id)
            if auth_constraint:
                try:
                    super().authorize(request=request,
                                      auth_constraint=auth_constraint,
                                      auth_action=action)
                except AuthValidationError as exp:
                    logger.warning("Request {} cannot be authorized by reason: {}".format(request, exp.reason))
                    raise UnauthorizedClientRequest(request.identifier,
                                                    request.reqId,
                                                    exp.reason)
                return True
            error_msg = "There is no authorization constraints for request: {}".format(request)
            logger.warning(error_msg)
            raise UnauthorizedClientRequest(request.identifier,
                                            request.reqId,
                                            error_msg)

    def create_auth_strategy(self):
        """depends on config"""
        return LocalAuthStrategy(self.auth_map)
