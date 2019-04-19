import pytest

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_cons_strategies import ConfigLedgerAuthStrategy
from indy_common.authorize.auth_constraints import AuthConstraint, ConstraintsSerializer
from indy_common.state import config
from plenum.common.constants import TRUSTEE
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture
def state():
    return PruningState(KeyValueStorageInMemory())


@pytest.fixture
def state_serializer():
    return ConstraintsSerializer(domain_state_serializer)


def test_config_strategy_get_constraint_from_state(state,
                                                   state_serializer):
    action_id = "1--2--3--4--5"
    constraint_to_state = AuthConstraint(role=TRUSTEE,
                                         sig_count=1,
                                         need_to_be_owner=True)
    constraint_to_map = AuthConstraint(role=TRUSTEE,
                                       sig_count=5,
                                       need_to_be_owner=False)
    auth_map = {action_id: constraint_to_map}
    state.set(config.make_state_path_for_auth_rule(action_id),
              state_serializer.serialize(constraint_to_state))
    strategy = ConfigLedgerAuthStrategy(auth_map=auth_map,
                                        state=state,
                                        serializer=state_serializer)
    from_state = strategy.get_auth_constraint(action_id)
    assert from_state != constraint_to_map
    assert from_state == constraint_to_state


def test_config_strategy_constraint_from_map(state,
                                             state_serializer):
    action_id = "1--2--3--4--5"
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=True)
    auth_map = {action_id: constraint}
    strategy = ConfigLedgerAuthStrategy(auth_map=auth_map,
                                        state=state,
                                        serializer=state_serializer)
    from_map = strategy.get_auth_constraint(action_id)
    assert from_map == constraint


def test_config_strategy_constraint_not_found(state,
                                              state_serializer):
    state_action_id = "1--2--3--4--5"
    test_action_id = "1--2--3--4--50"
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=True)
    auth_map = {state_action_id: constraint}
    state.set(config.make_state_path_for_auth_rule(state_action_id), state_serializer.serialize(constraint))
    strategy = ConfigLedgerAuthStrategy(auth_map=auth_map,
                                        state=state,
                                        serializer=state_serializer)
    from_state = strategy.get_auth_constraint(test_action_id)
    assert from_state is None
