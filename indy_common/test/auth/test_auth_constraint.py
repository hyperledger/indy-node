from indy_common.authorize.auth_constraints import AuthConstraint, AuthConstraintOr, AuthConstraintAnd
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
