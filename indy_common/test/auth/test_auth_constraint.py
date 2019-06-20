import copy

import pytest

from common.serializers.serialization import ledger_txn_serializer, domain_state_serializer
from indy_common.authorize.auth_constraints import AuthConstraint, AuthConstraintOr, AuthConstraintAnd, \
    ConstraintsSerializer, ROLE, CONSTRAINT_ID, ConstraintsEnum, NEED_TO_BE_OWNER, SIG_COUNT, METADATA, \
    ConstraintCreator, AUTH_CONSTRAINTS, AuthConstraintForbidden
from plenum.common.constants import TRUSTEE, STEWARD


def test_str_not_any_7_sig_owner():
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=7,
                                need_to_be_owner=True)
    assert str(constraint) == '7 TRUSTEE signatures are required and needs to be owner'


def test_str_not_any_7_sig_not_owner():
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=7,
                                need_to_be_owner=False)
    assert str(constraint) == '7 TRUSTEE signatures are required'


def test_str_not_any_1_sig_not_owner():
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=False)
    assert str(constraint) == '1 TRUSTEE signature is required'


def test_str_not_any_1_sig_owner():
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=True)
    assert str(constraint) == '1 TRUSTEE signature is required and needs to be owner'


def test_str_any_1_sig_owner():
    constraint = AuthConstraint(role="*",
                                sig_count=1,
                                need_to_be_owner=True)
    assert str(constraint) == '1 signature of any role is required and needs to be owner'


def test_str_any_1_sig_not_owner():
    constraint = AuthConstraint(role='*',
                                sig_count=1,
                                need_to_be_owner=False)
    assert str(constraint) == '1 signature of any role is required'


def test_str_any_several_sig_not_owner():
    constraint = AuthConstraint(role='*',
                                sig_count=7,
                                need_to_be_owner=False)
    assert str(constraint) == '7 signatures of any role are required'


def test_str_any_several_sig_owner():
    constraint = AuthConstraint(role='*',
                                sig_count=7,
                                need_to_be_owner=True)
    assert str(constraint) == '7 signatures of any role are required and needs to be owner'


def test_str_for_auth_constraint_or():
    constraint = AuthConstraintOr([AuthConstraint(role=TRUSTEE,
                                                  sig_count=1,
                                                  need_to_be_owner=True),
                                   AuthConstraint(role=STEWARD,
                                                  sig_count=1,
                                                  need_to_be_owner=True)])
    assert str(constraint) == '1 TRUSTEE signature is required and needs to be owner ' \
                              'OR ' \
                              '1 STEWARD signature is required and needs to be owner'


def test_str_for_auth_constraint_and():
    constraint = AuthConstraintAnd([AuthConstraint(role=TRUSTEE,
                                                   sig_count=1,
                                                   need_to_be_owner=True),
                                    AuthConstraint(role=STEWARD,
                                                   sig_count=1,
                                                   need_to_be_owner=True)])
    assert str(constraint) == '1 TRUSTEE signature is required and needs to be owner ' \
                              'AND ' \
                              '1 STEWARD signature is required and needs to be owner'


def test_str_for_auth_constraint_forbidden():
    constraint = AuthConstraintForbidden()
    assert str(constraint) == 'The action is forbidden'


@pytest.fixture
def constraints():
    role_constraints = [AuthConstraint(role=TRUSTEE,
                                       sig_count=1,
                                       need_to_be_owner=True),
                        AuthConstraint(role=STEWARD,
                                       sig_count=1,
                                       need_to_be_owner=True)]
    and_constraint = AuthConstraintAnd(role_constraints)
    or_constraint = AuthConstraintOr(role_constraints)
    forbidden_constraint = AuthConstraintForbidden()
    return role_constraints[0], and_constraint, or_constraint, forbidden_constraint


def test_check_equal(constraints):
    same_role, same_and, same_or, same_forbidden = constraints
    """
    The same constraints as from fixture but should have not the same id
    """
    role_constraints = [AuthConstraint(role=TRUSTEE,
                                       sig_count=1,
                                       need_to_be_owner=True),
                        AuthConstraint(role=STEWARD,
                                       sig_count=1,
                                       need_to_be_owner=True)]
    and_constraint = AuthConstraintAnd(role_constraints)
    or_constraint = AuthConstraintOr(role_constraints)
    forbidden_constraint = AuthConstraintForbidden()

    assert id(same_role) != id(role_constraints[0])
    assert id(same_or) != id(or_constraint)
    assert id(same_and) != id(and_constraint)
    assert id(same_forbidden) != id(forbidden_constraint)
    assert same_role == role_constraints[0]
    assert same_or == or_constraint
    assert same_and == and_constraint
    assert same_forbidden == forbidden_constraint


def test_constraint_serialization(constraints):
    constraint_serializer = ConstraintsSerializer(domain_state_serializer)
    for constraint in constraints:
        serialized = constraint_serializer.serialize(constraint)
        deserialized = constraint_serializer.deserialize(serialized)
        assert constraint == deserialized
        assert constraint_serializer.serialize(constraint) == \
            constraint_serializer.serialize(deserialized)


@pytest.fixture
def constraints_as_dict():
    trustee_role_as_dict = {
        CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
        ROLE: TRUSTEE,
        NEED_TO_BE_OWNER: True,
        SIG_COUNT: 1,
        METADATA: {}
    }
    steward_role_as_dict = {
        CONSTRAINT_ID: ConstraintsEnum.ROLE_CONSTRAINT_ID,
        ROLE: STEWARD,
        NEED_TO_BE_OWNER: True,
        SIG_COUNT: 1,
        METADATA: {}
    }
    and_as_dict = {
        CONSTRAINT_ID: ConstraintsEnum.AND_CONSTRAINT_ID,
        AUTH_CONSTRAINTS: [
            copy.copy(trustee_role_as_dict),
            copy.copy(steward_role_as_dict),
        ]
    }
    or_as_dict = {
        CONSTRAINT_ID: ConstraintsEnum.OR_CONSTRAINT_ID,
        AUTH_CONSTRAINTS: [
            copy.copy(trustee_role_as_dict),
            copy.copy(steward_role_as_dict)
        ]
    }
    forbidden_as_dict = {
        CONSTRAINT_ID: ConstraintsEnum.FORBIDDEN_CONSTRAINT_ID
    }
    return trustee_role_as_dict, and_as_dict, or_as_dict, forbidden_as_dict


# def test_error_on_deserialize():
#     constraint_serializer = ConstraintsSerializer(domain_state_serializer)
#     constraint_serializer.deserialize(b"some_string")


def test_constraint_creator(constraints_as_dict,
                            constraints):
    from_creator = [ConstraintCreator.create_constraint(c) for c in constraints_as_dict]
    assert all(map(lambda a, b: a == b, constraints, from_creator))
