from abc import abstractmethod, ABCMeta

from indy_common.authorize.auth_actions import split_action_id
from indy_common.authorize.auth_constraints import AbstractAuthConstraint, AbstractConstraintSerializer
from indy_common.state import config
from plenum.common.metrics_collector import MetricsName, MetricsCollector
from state.pruning_state import PruningState
from stp_core.common.log import getlogger

logger = getlogger()


class AbstractAuthStrategy(metaclass=ABCMeta):
    def __init__(self, auth_map):
        self.auth_map = auth_map

    @abstractmethod
    def get_auth_constraint(self, action_id) -> AbstractAuthConstraint:
        raise NotImplementedError()

    @abstractmethod
    def _find_auth_constraint_key(self, action_id, auth_map):
        raise NotImplementedError()

    @staticmethod
    def is_accepted_action_id(from_auth_map, from_req):
        am = split_action_id(from_auth_map)
        r = split_action_id(from_req)
        if r.prefix != am.prefix:
            return False
        if r.txn_type != am.txn_type:
            return False
        if r.field != am.field and \
                am.field != '*':
            return False
        if r.old_value != am.old_value and \
                am.old_value != '*':
            return False
        if r.new_value != am.new_value and \
                am.new_value != '*':
            return False
        return True


class LocalAuthStrategy(AbstractAuthStrategy):

    def get_auth_constraint(self, action_id) -> AbstractAuthConstraint:
        am_id = self._find_auth_constraint_key(action_id, self.auth_map)
        return self.auth_map.get(am_id)

    def _find_auth_constraint_key(self, action_id, auth_map):
        for am_id in auth_map.keys():
            if self.is_accepted_action_id(am_id, action_id):
                return am_id


class ConfigLedgerAuthStrategy(AbstractAuthStrategy):

    def __init__(self,
                 auth_map,
                 state: PruningState,
                 serializer: AbstractConstraintSerializer,
                 metrics: MetricsCollector = None):
        super().__init__(auth_map=auth_map)
        self.state = state
        self.serializer = serializer
        self.metrics = metrics
        self.from_state_count = 0

    def get_auth_constraint(self, action_id: str) -> AbstractAuthConstraint:
        """
        Find rule_id for incoming action_id and return AuthConstraint instance
        """
        return self._find_auth_constraint(action_id, self.auth_map)

    def _find_auth_constraint(self, action_id, auth_map):
        am_id = self._find_auth_constraint_key(action_id, auth_map)
        if am_id:
            constraint = self.get_from_state(key=config.make_state_path_for_auth_rule(am_id))
            if not constraint:
                return auth_map.get(am_id)
            logger.debug("Using auth constraint from state")
            if self.metrics:
                self.from_state_count += 1
                self.metrics.add_event(MetricsName.AUTH_RULES_FROM_STATE_COUNT, self.from_state_count)
            return constraint

    def _find_auth_constraint_key(self, action_id, auth_map):
        for am_id in auth_map.keys():
            if self.is_accepted_action_id(am_id, action_id):
                return am_id

    def get_from_state(self, key, isCommitted=False):
        from_state = self.state.get(key=key,
                                    isCommitted=isCommitted)
        if not from_state:
            return None
        return self.serializer.deserialize(from_state)
