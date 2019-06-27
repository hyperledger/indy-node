import pytest

from indy_common.constants import CONSTRAINT, AUTH_ACTION
from indy_common.types import ClientAuthRuleOperation
from indy_node.test.helper import generate_constraint_entity
from indy_node.test.auth_rule.helper import generate_constraint_list, \
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
    with pytest.raises(TypeError, match=AUTH_ACTION):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_entity_role():
    # ConstraintEntityField without required field 'role'
    invalid_auth_rule_operation = generate_auth_rule_operation()
    del invalid_auth_rule_operation[CONSTRAINT][ROLE]
    with pytest.raises(TypeError, match=ROLE):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_entity_role_in_extra_large_constraint():
    # ConstraintEntityField without required field 'role'
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_list(
                              auth_constraints=[generate_constraint_entity(),
                                                generate_constraint_entity()])]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS][1][AUTH_CONSTRAINTS][0][ROLE]
    with pytest.raises(TypeError, match=ROLE):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_auth_constraints():
    # ConstraintListField without required field 'auth_constraints'
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_entity()]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS]
    with pytest.raises(TypeError, match=AUTH_CONSTRAINTS):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_auth_constraints_with_large_constraint():
    # ConstraintListField without required field 'auth_constraints' on the 2nd level
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_list(
                              auth_constraints=[generate_constraint_entity(),
                                                generate_constraint_entity()])]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS][1][AUTH_CONSTRAINTS]
    with pytest.raises(TypeError, match=AUTH_CONSTRAINTS):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_constraint_id_with_large_constraint():
    # ConstraintListField without required field CONSTRAINT_ID on the 2nd level
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_list(
                              auth_constraints=[generate_constraint_entity(),
                                                generate_constraint_entity()])]))
    del invalid_auth_rule_operation[CONSTRAINT][AUTH_CONSTRAINTS][1][CONSTRAINT_ID]
    with pytest.raises(TypeError, match=CONSTRAINT_ID):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_with_empty_auth_constraints():
    # ConstraintListField without empty list in auth_constraints
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=generate_constraint_list(
        auth_constraints=[generate_constraint_entity(),
                          generate_constraint_list(
                              auth_constraints=[])]))
    with pytest.raises(TypeError, match="Fields {} should not be an empty "
                                        "list.".format(AUTH_CONSTRAINTS)):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_with_empty_constraint_list():
    # ClientAuthRuleOperation with empty list of constraints
    invalid_auth_rule_operation = generate_auth_rule_operation(constraint=[])
    with pytest.raises(TypeError, match="Fields {} and {} are required and should not "
                                        "be an empty list.".format(AUTH_CONSTRAINTS, CONSTRAINT)):
        validator.validate(invalid_auth_rule_operation)


def test_invalid_operation_without_none_constraint():
    # ConstraintListField without None in field CONSTRAINT
    invalid_auth_rule_operation = generate_auth_rule_operation()
    invalid_auth_rule_operation[CONSTRAINT] = None
    with pytest.raises(TypeError, match="Fields {} and {} are required and should not "
                                        "be an empty list.".format(AUTH_CONSTRAINTS, CONSTRAINT)):
        validator.validate(invalid_auth_rule_operation)
