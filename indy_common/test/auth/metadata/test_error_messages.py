import os
from collections import OrderedDict

import pytest

from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr
from indy_common.test.auth.metadata.helper import set_auth_constraint, PLUGIN_FIELD, build_req_and_action, Action
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.exceptions import UnauthorizedClientRequest

MAX_SIG_COUNT = 3


def test_plugin_simple_error_msg_no_plugin_field(write_auth_req_validator):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 2}))
    req, actions = build_req_and_action(Action(author=IDENTITY_OWNER, endorser=None,
                                               sigs={IDENTITY_OWNER: 1},
                                               is_owner=True,
                                               amount=None,
                                               extra_sigs=False))

    with pytest.raises(UnauthorizedClientRequest) as excinfo:
        write_auth_req_validator.validate(req, actions)
    assert ("missing required plugin field") in str(excinfo.value)


def test_plugin_simple_error_msg_extra_plugin_field(write_auth_req_validator):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True))
    req, actions = build_req_and_action(Action(author=IDENTITY_OWNER, endorser=None,
                                               sigs={IDENTITY_OWNER: 1},
                                               is_owner=True,
                                               amount=5,
                                               extra_sigs=False))

    with pytest.raises(UnauthorizedClientRequest) as excinfo:
        write_auth_req_validator.validate(req, actions)
    assert ("plugin field must be absent") in str(excinfo.value)


def test_plugin_simple_error_msg_not_enough_amount(write_auth_req_validator):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 10}))
    req, actions = build_req_and_action(Action(author=IDENTITY_OWNER, endorser=None,
                                               sigs={IDENTITY_OWNER: 1},
                                               is_owner=True,
                                               amount=5,
                                               extra_sigs=False))

    with pytest.raises(UnauthorizedClientRequest) as excinfo:
        write_auth_req_validator.validate(req, actions)
    assert ("not enough amount in plugin field") in str(excinfo.value)


def test_plugin_or_error_msg_not_enough_amount(write_auth_req_validator):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraintOr(auth_constraints=[
                            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False),
                            AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False,
                                           metadata={PLUGIN_FIELD: 10}),
                        ]))

    req, actions = build_req_and_action(Action(author=STEWARD, endorser=None,
                                               sigs={STEWARD: 1},
                                               is_owner=True,
                                               amount=5,
                                               extra_sigs=False))

    with pytest.raises(UnauthorizedClientRequest) as excinfo:
        write_auth_req_validator.validate(req, actions)
    expected = os.linesep.join([
        "Rule for this action is: 1 TRUSTEE signature is required OR 1 STEWARD signature is required with additional metadata new_field 10",
        "Failed checks:",
        "Constraint: 1 TRUSTEE signature is required, Error: Not enough TRUSTEE signatures",
        "Constraint: 1 STEWARD signature is required with additional metadata new_field 10, Error: not enough amount in plugin field"
    ])
    assert expected in str(excinfo.value.reason)


def test_plugin_or_error_msg_not_enough_amount_multiple_metadata_fields(write_auth_req_validator):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraintOr(auth_constraints=[
                            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False),
                            AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False,
                                           metadata=OrderedDict([
                                               (PLUGIN_FIELD, 10),
                                               ("aaa", "bbb")
                                           ]))
                        ]))
    req, actions = build_req_and_action(Action(author=STEWARD, endorser=None,
                                               sigs={STEWARD: 1},
                                               is_owner=True,
                                               amount=5,
                                               extra_sigs=False))

    with pytest.raises(UnauthorizedClientRequest) as excinfo:
        write_auth_req_validator.validate(req, actions)
    expected = os.linesep.join([
        "Rule for this action is: 1 TRUSTEE signature is required OR 1 STEWARD signature is required with additional metadata new_field 10 aaa bbb",
        "Failed checks:",
        "Constraint: 1 TRUSTEE signature is required, Error: Not enough TRUSTEE signatures",
        "Constraint: 1 STEWARD signature is required with additional metadata new_field 10 aaa bbb, Error: not enough amount in plugin field"
    ])
    assert expected in str(excinfo.value.reason)
