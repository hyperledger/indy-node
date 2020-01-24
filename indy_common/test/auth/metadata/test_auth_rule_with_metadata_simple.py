from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintForbidden
from indy_common.constants import ENDORSER
from indy_common.test.auth.metadata.helper import validate, PLUGIN_FIELD, Action
from plenum.common.constants import TRUSTEE

MAX_SIG_COUNT = 3


def test_plugin_simple_rule_1_sig_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                    signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=IDENTITY_OWNER, endorser=None, sigs={IDENTITY_OWNER: s},
                   is_owner=True, amount=2, extra_sigs=False)
            for s in range(1, MAX_SIG_COUNT + 1)
        ],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_owner_endorser(write_auth_req_validator, write_request_validation,
                                                 signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1, ENDORSER: s2},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_endorser_no_endorser(write_auth_req_validator, write_request_validation,
                                                       signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=ENDORSER, endorser=None, sigs={ENDORSER: s},
                   is_owner=True, amount=2, extra_sigs=True)
            for s in range(1, MAX_SIG_COUNT + 1)
        ],
        author=ENDORSER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_endorser_endorser(write_auth_req_validator, write_request_validation,
                                                    signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=ENDORSER, endorser=ENDORSER, sigs={ENDORSER: s},
                   is_owner=True, amount=2, extra_sigs=True)
            for s in range(1, MAX_SIG_COUNT + 1)
        ],
        author=ENDORSER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                      signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={ENDORSER: s1, TRUSTEE: s2},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_trustee_endorser(write_auth_req_validator, write_request_validation,
                                                   signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=ENDORSER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=ENDORSER, sigs={TRUSTEE: s2, ENDORSER: s3},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
            for s3 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=TRUSTEE, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_all_roles_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                              signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=IDENTITY_OWNER, endorser=None, sigs={IDENTITY_OWNER: s},
                   is_owner=True, amount=2, extra_sigs=False)
            for s in range(1, MAX_SIG_COUNT + 1)
        ],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_all_roles_owner_endorser(write_auth_req_validator, write_request_validation,
                                                           signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={IDENTITY_OWNER: s1, ENDORSER: s2},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_all_roles_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                                signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: s1},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_all_roles_trustee_endorser(write_auth_req_validator, write_request_validation,
                                                             signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=ENDORSER, sigs={TRUSTEE: s1, ENDORSER: s2},
                   is_owner=True, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
        ],
        author=TRUSTEE, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_3_sig_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                      signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=None, sigs={TRUSTEE: 3},
                   is_owner=owner, amount=2, extra_sigs=True)
            for owner in [True, False]],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_3_sig_trustee_endorser(write_auth_req_validator, write_request_validation,
                                                   signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=TRUSTEE, endorser=ENDORSER, sigs={TRUSTEE: 3, ENDORSER: s1},
                   is_owner=owner, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for owner in [True, False]
        ],
        author=TRUSTEE, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_3_sig_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                    signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_3_sig_owner_endorser(write_auth_req_validator, write_request_validation,
                                                 signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={TRUSTEE: 3, IDENTITY_OWNER: s1, ENDORSER: s2},
                   is_owner=owner, amount=2, extra_sigs=True)
            for s1 in range(1, MAX_SIG_COUNT + 1)
            for s2 in range(1, MAX_SIG_COUNT + 1)
            for owner in [True, False]
        ],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_0_sig_owner_no_endorser(write_auth_req_validator, write_request_validation,
                                                    signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=0, need_to_be_owner=False,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=None, sigs={},
                              is_owner=owner, amount=2, extra_sigs=False)
                       for owner in [True, False]] + [
            Action(author=IDENTITY_OWNER, endorser=None, sigs={IDENTITY_OWNER: s},
                   is_owner=owner, amount=2, extra_sigs=False)
            for owner in [True, False]
            for s in range(1, MAX_SIG_COUNT + 1)],
        author=IDENTITY_OWNER, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_0_sig_owner_endorser(write_auth_req_validator, write_request_validation,
                                                 signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=0, need_to_be_owner=False,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[Action(author=IDENTITY_OWNER, endorser=ENDORSER, sigs={ENDORSER: s},
                              is_owner=owner, amount=2, extra_sigs=True)
                       for s in range(1, MAX_SIG_COUNT + 1)
                       for owner in [True, False]],
        author=IDENTITY_OWNER, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_0_sig_trustee_no_endorser(write_auth_req_validator, write_request_validation,
                                                      signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=0, need_to_be_owner=False,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[Action(author=TRUSTEE, endorser=None, sigs=signature,
                              is_owner=owner, amount=2, extra_sigs=True)
                       for signature in signatures
                       for owner in [True, False]],
        author=TRUSTEE, endorser=None,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_0_sig_trustee_endorser(write_auth_req_validator, write_request_validation,
                                                   signatures, is_owner, off_ledger_signature, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=0, need_to_be_owner=False,
                                       off_ledger_signature=off_ledger_signature,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[Action(author=TRUSTEE, endorser=ENDORSER, sigs={ENDORSER: s},
                              is_owner=owner, amount=2, extra_sigs=True)
                       for s in range(1, MAX_SIG_COUNT + 1)
                       for owner in [True, False]],
        author=TRUSTEE, endorser=ENDORSER,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_not_allowed(write_auth_req_validator, write_request_validation,
                                        author, endorser, signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraintForbidden(),
        valid_actions=[],
        author=author, endorser=endorser,
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )
