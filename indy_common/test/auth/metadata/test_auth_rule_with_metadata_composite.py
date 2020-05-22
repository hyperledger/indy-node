from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr, AuthConstraintAnd
from indy_common.constants import ENDORSER
from indy_common.test.auth.metadata.helper import validate, PLUGIN_FIELD, Action
from plenum.common.constants import TRUSTEE, STEWARD

MAX_SIG_COUNT = 3


def test_plugin_or_rule_all_amount_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                       signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 1}),
            AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=True,
                           metadata={PLUGIN_FIELD: 3}),
        ]),
        valid_actions=[Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s}, is_owner=owner, amount=1,
                              extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]
                       ] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1,
                                                        STEWARD: s2},
                   is_owner=owner, amount=2, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(1, 4)
            for owner in [True, False]] + [
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1, ENDORSER: s2},
                   is_owner=True, amount=3, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(1, 4)],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_same_role_endorser_no_endorser(write_auth_req_validator, write_request_validation,
                                                                  signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
        ]),
        valid_actions=[Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s},
                              is_owner=owner, amount=amount, extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]
                       for amount in [2, None]],
        author=ENDORSER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_same_role_endorser_endorser(write_auth_req_validator, write_request_validation,
                                                               signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
        ]),
        valid_actions=[Action(author=ENDORSER, endorser=ENDORSER, sigs={ENDORSER: s},
                              is_owner=owner, amount=amount, extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]
                       for amount in [2, None]],
        author=ENDORSER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_same_role_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                               signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
        ]),
        valid_actions=[],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_same_role_owner_endorser(write_auth_req_validator, write_request_validation,
                                                            signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={ENDORSER: s1, IDENTITY_OWNER: s2},
                              is_owner=owner, amount=amount, extra_sigs=True)
                       for s1 in range(1, 4)
                       for s2 in range(1, 4)
                       for owner in [True, False]
                       for amount in [2, None]],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_diff_roles_endorser_no_endorser(write_auth_req_validator, write_request_validation,
                                                                   signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s},
                              is_owner=owner, amount=None, extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s1,
                                                         IDENTITY_OWNER: s2},
                   is_owner=True, amount=1, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(1, 4)],
        author=ENDORSER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_diff_roles_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                                signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=None, sigs={IDENTITY_OWNER: s},
                              is_owner=True, amount=1, extra_sigs=False)
                       for s in range(1, MAX_SIG_COUNT + 1)],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_diff_roles_owner_endorser(write_auth_req_validator, write_request_validation,
                                                             signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1, ENDORSER: s2},
                              is_owner=owner, amount=None, extra_sigs=True)
                       for s1 in range(1, 4)
                       for s2 in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1,
                                                                   ENDORSER: s2},
                   is_owner=True, amount=1, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(1, 4)],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_all_roles_endorser_no_endorser(write_auth_req_validator, write_request_validation,
                                                                  signatures, is_owner, amount, off_ledger_signature):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                           off_ledger_signature=off_ledger_signature,
                           metadata={PLUGIN_FIELD: 3}),
        ]),
        valid_actions=[Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s},
                              is_owner=owner, amount=None, extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s}, is_owner=True, amount=3, extra_sigs=True)
            for s in range(1, 4)],
        author=ENDORSER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_all_roles_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                               signatures, is_owner, amount, off_ledger_signature):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                           off_ledger_signature=off_ledger_signature,
                           metadata={PLUGIN_FIELD: 3}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=None, sigs={IDENTITY_OWNER: s},
                              is_owner=True, amount=3, extra_sigs=False)
                       for s in range(1, MAX_SIG_COUNT + 1)],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_one_amount_all_roles_owner_endorser(write_auth_req_validator, write_request_validation,
                                                            signatures, is_owner, amount, off_ledger_signature):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                           off_ledger_signature=off_ledger_signature,
                           metadata={PLUGIN_FIELD: 3}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1, ENDORSER: s2},
                              is_owner=owner, amount=None, extra_sigs=True)
                       for s1 in range(1, 4)
                       for s2 in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1, ENDORSER: s2},
                   is_owner=True, amount=3, extra_sigs=True)
            for s1 in range(1, 4)
            for s2 in range(1, 4)],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_diff_amount_same_role_endorser_no_endorser(write_auth_req_validator, write_request_validation,
                                                                   signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
            AuthConstraint(role=ENDORSER, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: 2},
                   is_owner=True, amount=2, extra_sigs=True),
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: 3},
                   is_owner=True, amount=1, extra_sigs=True),
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: 2},
                   is_owner=False, amount=2, extra_sigs=True),
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: 3},
                   is_owner=False, amount=1, extra_sigs=True)
        ],
        author=ENDORSER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_diff_amount_same_role_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                                signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
            AuthConstraint(role=ENDORSER, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_rule_diff_amount_same_role_owner_endorser(write_auth_req_validator, write_request_validation,
                                                             signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=ENDORSER, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
            AuthConstraint(role=ENDORSER, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 1}),
        ]),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s, ENDORSER: 2},
                              is_owner=owner, amount=2, extra_sigs=True)
                       for s in range(1, 4)
                       for owner in [True, False]] + [
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s,
                                                                   ENDORSER: 3},
                   is_owner=owner, amount=1, extra_sigs=True)
            for s in range(1, 4)
            for owner in [True, False]],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_and_rule_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                             signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2}),
            AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 2})
        ]),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s, STEWARD: 3},
                   is_owner=owner, amount=2, extra_sigs=True)
            for s in range(2, 4)
            for owner in [True, False]
        ],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )
