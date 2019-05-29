from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr, AuthConstraintAnd
from indy_common.constants import TRUST_ANCHOR
from indy_common.test.auth.metadata.helper import validate, PLUGIN_FIELD
from plenum.common.constants import TRUSTEE, STEWARD

MAX_SIG_COUNT = 3


def test_plugin_simple_rule_1_sig(write_auth_req_validator, write_request_validation,
                                  signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            ({IDENTITY_OWNER: 1}, True, 2),
            ({IDENTITY_OWNER: 2}, True, 2),
            ({IDENTITY_OWNER: 3}, True, 2)
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_1_sig_all_roles(write_auth_req_validator, write_request_validation,
                                            signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            (signature, True, 2) for signature in signatures if signature
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_3_sig(write_auth_req_validator, write_request_validation,
                                  signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[
            ({TRUSTEE: 3}, False, 2),
            ({TRUSTEE: 3}, True, 2),
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_0_sig(write_auth_req_validator, write_request_validation,
                                  signatures, is_owner, amount):
    validate(
        auth_constraint=AuthConstraint(role='*', sig_count=0, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 2}),
        valid_actions=[(signature, True, 2) for signature in signatures] +
                      [(signature, False, 2) for signature in signatures],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_simple_rule_not_allowed(write_auth_req_validator, write_request_validation,
                                        signatures, is_owner, amount):
    validate(
        auth_constraint=None,
        valid_actions=[],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )
