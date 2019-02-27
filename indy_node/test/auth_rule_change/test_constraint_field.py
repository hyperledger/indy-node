import pytest

from indy_common.constants import CONSTRAINT, AUTH_ACTION
from indy_common.types import ClientAuthRuleOperation
from indy_node.test.auth_rule_change.helper import generate_constraint_entity, generate_constraint_list, \
    generate_auth_rule_operation
from indy_common.authorize.auth_constraints import ROLE, AUTH_CONSTRAINTS, CONSTRAINT_ID

validator = ClientAuthRuleOperation()

valid_auth_rule_operation_small = generate_auth_rule_operation()
valid_auth_rule_operation_large = generate_auth_rule_operation(constraint=generate_constraint_list(
    auth_constraints=[generate_constraint_entity(),
                      generate_constraint_entity()]))
valid_auth_rule_operation_extra_large = generate_auth_rule_operation(constraint=generate_constraint_list(
    auth_constraints=[generate_constraint_entity(),
                      generate_constraint_list(
                          auth_constraints=[generate_constraint_entity(),
                                            generate_constraint_entity()])]))


def test_valid():
    validator.validate(valid_auth_rule_operation_small)
    validator.validate(valid_auth_rule_operation_large)
    validator.validate(valid_auth_rule_operation_extra_large)


def test_invalid_operation_action():
    # must be ADD_PREFIX or EDIT_PREFIX
    invalid_auth_rule_operation = generate_auth_rule_operation(auth_action="auth_action")
    with pytest.raises(TypeError) as e:
        validator.validate(invalid_auth_rule_operation)
    e.match(AUTH_ACTION)


def test_invalid_entity_role():
    # ConstraintEntityField without required field 'role'
    invalid_auth_rule_operation = generate_auth_rule_operation()
    del invalid_auth_rule_operation[CONSTRAINT][ROLE]
    with pytest.raises(TypeError) as e:
        validator.validate(invalid_auth_rule_operation)
    e.match(ROLE)


def test_invalid_operation_auth_constraints():
    # ConstraintListField without required field 'auth_constraints'
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_entity()]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS]
    with pytest.raises(TypeError) as e:
        validator.validate(invalid_auth_rule_operation)
    e.match(AUTH_CONSTRAINTS)


def test_invalid_operation_auth_constraints_with_large_constraint():
    # ConstraintListField without required field 'auth_constraints' on the 2nd level
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_list(
                              auth_constraints=[generate_constraint_entity(),
                                                generate_constraint_entity()])]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS][1][AUTH_CONSTRAINTS]
    with pytest.raises(TypeError) as e:
        validator.validate(invalid_auth_rule_operation)
    e.match(AUTH_CONSTRAINTS)

