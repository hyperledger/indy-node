from abc import abstractmethod

from indy_common.authorize.auth_cons_strategies import LocalAuthStrategy, ConfigLedgerAuthStrategy
from indy_common.authorize.auth_actions import AbstractAuthAction
from indy_common.authorize.auth_constraints import ConstraintsEnum, AbstractConstraintSerializer
from indy_common.authorize.authorizer import AbstractAuthorizer, CompositeAuthorizer, RolesAuthorizer, AndAuthorizer, \
    OrAuthorizer, AuthValidationError
from indy_common.constants import LOCAL_AUTH_POLICY, CONFIG_LEDGER_AUTH_POLICY
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.metrics_collector import MetricsCollector
from state.pruning_state import PruningState
from stp_core.common.log import getlogger


logger = getlogger()


class AbstractRequestValidator(AbstractAuthorizer):

    @abstractmethod
    def validate(self, request, action_list: [AbstractAuthAction]):
        raise NotImplementedError()


class WriteRequestValidator(AbstractRequestValidator, CompositeAuthorizer):
    def __init__(self,
                 config,
                 auth_map: dict,
                 cache: IdrCache,
                 config_state: PruningState,
                 state_serializer: AbstractConstraintSerializer,
                 anyone_can_write_map=None,
                 metrics: MetricsCollector=None):
        CompositeAuthorizer.__init__(self)
        self.config = config
        self.auth_map = auth_map
        self.cache = cache
        self.config_state = config_state
        self.state_serializer = state_serializer
        self.anyone_can_write_map = anyone_can_write_map
        self.metrics = metrics

        self.anyone_can_write = self.config.ANYONE_CAN_WRITE
        self.auth_cons_strategy = self.create_auth_strategy()
        self.register_default_authorizers()

    def register_default_authorizers(self):
        self.register_authorizer(RolesAuthorizer(cache=self.cache), auth_constraint_id=ConstraintsEnum.ROLE_CONSTRAINT_ID)
        self.register_authorizer(AndAuthorizer(), auth_constraint_id=ConstraintsEnum.AND_CONSTRAINT_ID)
        self.register_authorizer(OrAuthorizer(), auth_constraint_id=ConstraintsEnum.OR_CONSTRAINT_ID)

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
            error_msg = 'Request can not be authorized as action is not allowed: {}'.format(request)
            logger.warning(error_msg)
            raise UnauthorizedClientRequest(request.identifier,
                                            request.reqId,
                                            error_msg)

    def create_auth_strategy(self):
        """depends on config"""
        if self.config.authPolicy == LOCAL_AUTH_POLICY:
            return LocalAuthStrategy(auth_map=self.auth_map,
                                     anyone_can_write_map=self.anyone_can_write_map if self.anyone_can_write else None)
        elif self.config.authPolicy == CONFIG_LEDGER_AUTH_POLICY:
            return ConfigLedgerAuthStrategy(auth_map=self.auth_map,
                                            state=self.config_state,
                                            serializer=self.state_serializer,
                                            anyone_can_write_map=self.anyone_can_write_map if self.anyone_can_write else None,
                                            metrics=self.metrics)
