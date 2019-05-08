from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr, AuthConstraintAnd
from indy_common.constants import TRUST_ANCHOR
from indy_common.test.auth.metadata.helper import validate, PLUGIN_FIELD
from plenum.common.constants import TRUSTEE, STEWARD

MAX_SIG_COUNT = 3


def test_plugin_and_or_rule_same_role(write_auth_req_validator, write_request_validation,
                                      signatures, is_owner, amount):
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
            ({TRUSTEE: 2, STEWARD: 3}, False, 2),
            ({TRUSTEE: 3, STEWARD: 3}, False, 2),

            ({TRUSTEE: 2, STEWARD: 3}, True, 2),
            ({TRUSTEE: 3, STEWARD: 3}, True, 2),

            ({TRUSTEE: 2, STEWARD: 3}, False, None),
            ({TRUSTEE: 3, STEWARD: 3}, False, None),

            ({TRUSTEE: 2, STEWARD: 3}, True, None),
            ({TRUSTEE: 3, STEWARD: 3}, True, None),
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_and_or_rule_diff_role(write_auth_req_validator, write_request_validation,
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
                AuthConstraint(role=TRUST_ANCHOR, sig_count=3, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 3}),
            ])
        ]),
        valid_actions=[
            ({TRUSTEE: 2, TRUST_ANCHOR: 3}, False, 3),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, False, 3),
            ({TRUSTEE: 2, TRUST_ANCHOR: 3}, True, 3),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, True, 3),

            ({TRUSTEE: 2, IDENTITY_OWNER: 3}, True, 3),
            ({TRUSTEE: 3, IDENTITY_OWNER: 3}, True, 3),

            ({STEWARD: 2, TRUST_ANCHOR: 3}, False, 3),
            ({STEWARD: 3, TRUST_ANCHOR: 3}, False, 3),
            ({STEWARD: 2, TRUST_ANCHOR: 3}, True, 3),
            ({STEWARD: 3, TRUST_ANCHOR: 3}, True, 3),

            ({STEWARD: 2, IDENTITY_OWNER: 3}, True, 3),
            ({STEWARD: 3, IDENTITY_OWNER: 3}, True, 3),
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_or_and_rule_diff_roles(write_auth_req_validator, write_request_validation,
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
                AuthConstraint(role=TRUST_ANCHOR, sig_count=2, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 2}),
            ]),
            AuthConstraintAnd(auth_constraints=[
                AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                               metadata={PLUGIN_FIELD: 3}),
                AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=True,
                               metadata={PLUGIN_FIELD: 3}),
            ]),
        ]),
        valid_actions=[
            ({TRUSTEE: 3}, False, None),
            ({TRUSTEE: 3}, True, None),

            ({TRUSTEE: 1, STEWARD: 2}, False, None),
            ({TRUSTEE: 2, STEWARD: 2}, False, None),
            ({TRUSTEE: 1, STEWARD: 3}, False, None),
            ({TRUSTEE: 2, STEWARD: 3}, False, None),
            ({TRUSTEE: 3, STEWARD: 3}, False, None),

            ({TRUSTEE: 1, STEWARD: 2}, True, None),
            ({TRUSTEE: 2, STEWARD: 2}, True, None),
            ({TRUSTEE: 1, STEWARD: 3}, True, None),
            ({TRUSTEE: 2, STEWARD: 3}, True, None),
            ({TRUSTEE: 3, STEWARD: 3}, True, None),

            ({TRUSTEE: 1, TRUST_ANCHOR: 2}, True, 2),
            ({TRUSTEE: 2, TRUST_ANCHOR: 2}, True, 2),
            ({TRUSTEE: 1, TRUST_ANCHOR: 3}, True, 2),
            ({TRUSTEE: 2, TRUST_ANCHOR: 3}, True, 2),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, True, 2),

            ({TRUSTEE: 2, IDENTITY_OWNER: 3}, True, 3),
            ({TRUSTEE: 3, IDENTITY_OWNER: 3}, True, 3),
        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )


def test_plugin_complex(write_auth_req_validator, write_request_validation,
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
                        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 1}),
                    ]),
                    AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False,
                                   metadata={PLUGIN_FIELD: 1}),
                    AuthConstraint(role=TRUST_ANCHOR, sig_count=2, need_to_be_owner=False,
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
                    AuthConstraint(role=TRUST_ANCHOR, sig_count=2, need_to_be_owner=True),
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
        valid_actions=[
            # 1st
            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 1}, False, 1),
            ({TRUSTEE: 3, STEWARD: 2, TRUST_ANCHOR: 1}, False, 1),
            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 2}, False, 1),
            ({TRUSTEE: 3, STEWARD: 2, TRUST_ANCHOR: 2}, False, 1),
            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 3}, False, 1),
            ({TRUSTEE: 3, STEWARD: 3, TRUST_ANCHOR: 1}, False, 1),
            ({TRUSTEE: 3, STEWARD: 3, TRUST_ANCHOR: 3}, False, 1),

            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 1}, True, 1),
            ({TRUSTEE: 3, STEWARD: 2, TRUST_ANCHOR: 1}, True, 1),
            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 2}, True, 1),
            ({TRUSTEE: 3, STEWARD: 2, TRUST_ANCHOR: 2}, True, 1),
            ({TRUSTEE: 3, STEWARD: 1, TRUST_ANCHOR: 3}, True, 1),
            ({TRUSTEE: 3, STEWARD: 3, TRUST_ANCHOR: 1}, True, 1),
            ({TRUSTEE: 3, STEWARD: 3, TRUST_ANCHOR: 3}, True, 1),

            ({TRUSTEE: 3, STEWARD: 2}, False, 1),
            ({TRUSTEE: 3, STEWARD: 3}, False, 1),
            ({TRUSTEE: 3, STEWARD: 2}, True, 1),
            ({TRUSTEE: 3, STEWARD: 3}, True, 1),

            ({TRUSTEE: 3, TRUST_ANCHOR: 2}, False, 1),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, False, 1),
            ({TRUSTEE: 3, TRUST_ANCHOR: 2}, True, 1),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, True, 1),

            # 2d
            ({TRUSTEE: 3, IDENTITY_OWNER: 1}, True, 3),
            ({TRUSTEE: 3, IDENTITY_OWNER: 2}, True, 3),
            ({TRUSTEE: 3, IDENTITY_OWNER: 3}, True, 3),

            # 3d
            ({TRUSTEE: 3, STEWARD: 2}, False, None),
            ({TRUSTEE: 3, STEWARD: 3}, False, None),
            ({TRUSTEE: 3, STEWARD: 2}, True, None),
            ({TRUSTEE: 3, STEWARD: 3}, True, None),

            ({TRUSTEE: 3, TRUST_ANCHOR: 2}, False, None),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, False, None),
            ({TRUSTEE: 3, TRUST_ANCHOR: 2}, True, None),
            ({TRUSTEE: 3, TRUST_ANCHOR: 3}, True, None),

            # 4th
            ({TRUSTEE: 2, IDENTITY_OWNER: 1}, True, 2),
            ({TRUSTEE: 2, IDENTITY_OWNER: 2}, True, 2),
            ({TRUSTEE: 2, IDENTITY_OWNER: 3}, True, 2),
            ({TRUSTEE: 3, IDENTITY_OWNER: 1}, True, 2),
            ({TRUSTEE: 3, IDENTITY_OWNER: 2}, True, 2),
            ({TRUSTEE: 3, IDENTITY_OWNER: 3}, True, 2),

        ],
        all_signatures=signatures, is_owner=is_owner, amount=amount,
        write_auth_req_validator=write_auth_req_validator,
        write_request_validation=write_request_validation
    )
