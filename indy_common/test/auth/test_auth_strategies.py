import pytest

from common.exceptions import LogicError
from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_cons_strategies import LocalAuthStrategy, AbstractAuthStrategy, ConfigLedgerAuthStrategy
from indy_common.authorize.auth_constraints import AuthConstraint, ConstraintsSerializer
from plenum.common.constants import TRUSTEE, STEWARD
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope='function')
def auth_map(action_add, action_edit):
    """
    action_ids:
    for add: "ADD--SomeType--some_field--*--new_value"
    for edit: "EDIT--SomeType--some_field--old_value--new_value"
    """
    return {action_add.get_action_id(): AuthConstraint(role=STEWARD,
                                                       sig_count=3),
            action_edit.get_action_id(): AuthConstraint(role=STEWARD,
                                                        sig_count=2)}


@pytest.fixture(scope='function')
def local_auth_strategy(auth_map):
    return LocalAuthStrategy(auth_map=auth_map)


def test_local_strategy_found_the_same_action_id(local_auth_strategy):
    assert local_auth_strategy.get_auth_constraint("ADD--SomeType--some_field--*--new_value")
    assert local_auth_strategy.get_auth_constraint("EDIT--SomeType--some_field--old_value--new_value")


def test_local_strategy_not_found_action_id(local_auth_strategy):
    assert local_auth_strategy.get_auth_constraint("ADD--SomeType--some_field--*--other_new_value") is None
    assert local_auth_strategy.get_auth_constraint("EDIT--SomeType--some_field--old_value--other_new_value") is None


"""Group of tests for checking is_accepted method"""


@pytest.fixture(scope='module')
def is_accepted():
    return AbstractAuthStrategy.is_accepted_action_id


@pytest.fixture
def config_ledger_strategy(state, state_serializer):
    return ConfigLedgerAuthStrategy(auth_map,
                                    state=state,
                                    serializer=state_serializer)


def test_is_accepted_by_the_same(is_accepted):
    assert is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                       "PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_not_is_accepted_by_prefix(is_accepted):
    assert not is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                           "aaPREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_not_is_accepted_by_type(is_accepted):
    assert not is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                           "PREFIX--aaTYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_not_is_accepted_by_field(is_accepted):
    assert not is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                           "PREFIX--TYPE--aaFIELD--OLD_VALUE--NEW_VALUE")


def test_not_is_accepted_by_old_value(is_accepted):
    assert not is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                           "PREFIX--TYPE--FIELD--aaOLD_VALUE--NEW_VALUE")


def test_not_is_accepted_by_new_value(is_accepted):
    assert not is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE",
                           "PREFIX--TYPE--FIELD--OLD_VALUE--aaNEW_VALUE")


def test_is_accepted_for_all_field(is_accepted):
    assert is_accepted("PREFIX--TYPE--*--OLD_VALUE--NEW_VALUE",
                       "PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_is_accepted_for_all_old_value(is_accepted):
    assert is_accepted("PREFIX--TYPE--FIELD--*--NEW_VALUE",
                       "PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_is_accepted_for_all_new_value(is_accepted):
    assert is_accepted("PREFIX--TYPE--FIELD--OLD_VALUE--*",
                       "PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")


def test_is_accepted_for_all(is_accepted):
    assert is_accepted("PREFIX--TYPE--*--*--*",
                       "PREFIX--TYPE--FIELD--OLD_VALUE--NEW_VALUE")
