import pytest

from indy_common.auth_rules import AuthConstraint, RoleDef


@pytest.fixture(scope='function')
def auth_constraint():
    return AuthConstraint([RoleDef('TRUSTEE', 3),
                           RoleDef('STEWARD', 7)])


def test_accepted_exactly_other_constraint(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 3),
                                          RoleDef('STEWARD', 7)])
    assert auth_constraint.is_accepted(checking_constraint)


def test_accepted_more_trustees(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 4),
                                          RoleDef('STEWARD', 7)])
    assert auth_constraint.is_accepted(checking_constraint)


def test_accepted_more_stewards(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 3),
                                          RoleDef('STEWARD', 10)])
    assert auth_constraint.is_accepted(checking_constraint)


def test_not_accepted_less_trustees(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 2),
                                          RoleDef('STEWARD', 7)])
    assert not auth_constraint.is_accepted(checking_constraint)


def test_not_accepted_less_stewards(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 3),
                                          RoleDef('STEWARD', 6)])
    assert not auth_constraint.is_accepted(checking_constraint)


def test_not_accepted_without_stewards(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('TRUSTEE', 3)])
    assert not auth_constraint.is_accepted(checking_constraint)


def test_not_accepted_without_trustees(auth_constraint):
    checking_constraint = AuthConstraint([RoleDef('STEWARD', 7)])
    assert not auth_constraint.is_accepted(checking_constraint)