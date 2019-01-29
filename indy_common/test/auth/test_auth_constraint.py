from indy_common.authorize.auth_constraints import AuthConstraint, AuthConstraintOr, AuthConstraintAnd
from plenum.common.constants import TRUSTEE, STEWARD


def test_str_for_auth_constraint():
    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=True)
    assert str(constraint) == 'Required role: TRUSTEE, Count of signatures: 1, Need to be owner: True'


def test_str_for_auth_constraint_or():
    constraint = AuthConstraintOr([AuthConstraint(role=TRUSTEE,
                                                  sig_count=1,
                                                  need_to_be_owner=True),
                                   AuthConstraint(role=STEWARD,
                                                  sig_count=1,
                                                  need_to_be_owner=True)])
    assert str(constraint) == 'Required role: TRUSTEE, Count of signatures: 1, Need to be owner: True ' \
                              'OR ' \
                              'Required role: STEWARD, Count of signatures: 1, Need to be owner: True'


def test_str_for_auth_constraint_and():
    constraint = AuthConstraintAnd([AuthConstraint(role=TRUSTEE,
                                                   sig_count=1,
                                                   need_to_be_owner=True),
                                    AuthConstraint(role=STEWARD,
                                                   sig_count=1,
                                                   need_to_be_owner=True)])
    assert str(constraint) == 'Required role: TRUSTEE, Count of signatures: 1, Need to be owner: True ' \
                              'AND ' \
                              'Required role: STEWARD, Count of signatures: 1, Need to be owner: True'
