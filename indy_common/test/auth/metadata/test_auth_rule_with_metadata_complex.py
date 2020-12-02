from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr, AuthConstraintAnd, \
    AuthConstraintForbidden
from indy_common.constants import ENDORSER
from indy_common.test.auth.metadata.helper import validate, PLUGIN_FIELD, Action
from plenum.common.constants import TRUSTEE, STEWARD

MAX_SIG_COUNT = 3


def test_plugin_and_or_rule_same_role_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                          signatures, amount):
    validate(
        auth_constraint=AuthConstraintAnd(auth_constraints=[
            AuthConstraintOr(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False),
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 2}),
            ]),
            AuthConstraintOr(auth_constraints=[
                AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False),
                AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 2}),
            ])
        ]),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 2, STEWARD: 3},
                   is_owner=False, amount=2, extra_sigs=True),
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, STEWARD: 3},
                   is_owner=False, amount=2, extra_sigs=True),

            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 2, STEWARD: 3},
                   is_owner=False, amount=None, extra_sigs=True),
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, STEWARD: 3},
                   is_owner=False, amount=None, extra_sigs=True),
        ],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=False, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_and_or_rule_diff_role_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                          signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintAnd(auth_constraints=[
            AuthConstraintOr(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
            ]),
            AuthConstraintOr(auth_constraints=[
                AuthConstraint(role=ENDORSER, sig_count=3, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 3}),
            ])
        ]),
        valid_actions=[Action(author=TRUSTEE, endorser=None, sigs={ENDORSER: 3, TRUSTEE: s},
                              is_owner=owner, amount=3, extra_sigs=True)
                       for s in range(2, 4)
                       for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={STEWARD: s1,
                                                        ENDORSER: 3,
                                                        TRUSTEE: s2},
                   is_owner=owner, amount=3, extra_sigs=True)
            for s1 in range(2, 4)
            for s2 in range(1, MAX_SIG_COUNT + 1)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={STEWARD: s1,
                                                        IDENTITY_OWNER: 3,
                                                        TRUSTEE: s2},
                   is_owner=True, amount=3, extra_sigs=True)
            for s1 in range(2, 4)
            for s2 in range(1, MAX_SIG_COUNT + 1)],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_and_rule_diff_roles_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                           signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False),
            ]),
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False),
                AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False),
            ]),
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 2}),
                AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 2}),
            ]),
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 3}),
            ]),
        ]),
        valid_actions=[Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3},
                              is_owner=False, amount=None, extra_sigs=True),
                       Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3},
                              is_owner=True, amount=None, extra_sigs=True)] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1, STEWARD: s2},
                   is_owner=owner, amount=None, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(2, 4)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1, ENDORSER: s2},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, 4) for s2 in range(2, 4)] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 2, IDENTITY_OWNER: 3},
                   is_owner=True, amount=3, extra_sigs=True),
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, IDENTITY_OWNER: 3},
                   is_owner=True, amount=3, extra_sigs=True)],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_complex_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                            signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            # 1st
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 1}),
                AuthConstraintOr(auth_constraints=[
                    AuthConstraintAnd(auth_constraints=[
                        AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 1}),
                        AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 1}),
                    ]),
                    AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False,
                                   metadata={PLUGIN_FIELD: 1}),
                    AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=False,
                                   metadata={PLUGIN_FIELD: 1}),
                ])
            ]),
            # 2d
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 3})
            ]),
            # 3d
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False),
                AuthConstraintOr(auth_constraints=[
                    AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False),
                    AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=True),
                ])
            ]),
            # 4th
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 2}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 2})
            ]),
        ]),
        valid_actions=[Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, STEWARD: s1, ENDORSER: s2},  # 1st
                              is_owner=owner, amount=1, extra_sigs=True)
                       for s1 in range(1, 4)
                       for s2 in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, STEWARD: s},
                   is_owner=owner, amount=1, extra_sigs=True)
            for s in range(2, 4)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, IDENTITY_OWNER: s},  # 2d
                   is_owner=True, amount=3, extra_sigs=True)
            for s in range(1, 4)] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, STEWARD: s},  # 3d
                   is_owner=owner, amount=None, extra_sigs=True)
            for s in range(2, 4)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3, ENDORSER: s},
                   is_owner=owner, amount=None, extra_sigs=True)
            for s in range(2, 4)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 2, IDENTITY_OWNER: s},  # 4th
                   is_owner=True, amount=2, extra_sigs=True)
            for s in range(1, 4)],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_complex_with_and_rule_with_not_allowed(write_auth_req_validator, write_request_validation,
                                                       signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraintAnd(auth_constraints=[
            AuthConstraintForbidden(),
            AuthConstraint(role="*", sig_count=1, need_to_be_owner=False,
                           off_ledger_signature=off_ledger_signature,
                           metadata={PLUGIN_FIELD: 2})
        ]),
        valid_actions=[],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_complex_with_or_rule_with_not_allowed_trustee_no_endorser(write_auth_req_validator,
                                                                          write_request_validation,
                                                                          signatures, is_owner, off_ledger_signature,
                                                                          amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraintForbidden(),
            AuthConstraint(role="*", sig_count=1, need_to_be_owner=False,
                           off_ledger_signature=off_ledger_signature,
                           metadata={PLUGIN_FIELD: 2})
        ]),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1},
                   is_owner=owner, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for owner in [True, False]
        ],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )
