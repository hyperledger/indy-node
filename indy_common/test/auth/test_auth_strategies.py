import pytest

from indy_common.auth_cons_strategies import LocalAuthStrategy
from indy_common.auth_constraints import AuthConstraint


@pytest.fixture(scope='function')
def auth_map(action_add, action_edit):
    """
    action_ids:
    for add: "ADD--SomeType--some_field--*--new_value"
    for edit: "EDIT--SomeType--some_field--old_value--new_value"
    """
    return {action_add.get_action_id(): AuthConstraint(role="Actor",
                                                       sig_count=3),
            action_edit.get_action_id(): AuthConstraint(role="Actor",
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
