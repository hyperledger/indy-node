import pytest

from indy_common.authorize.auth_actions import AbstractAuthAction, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER, AuthConstraintOr, AuthConstraintAnd
from indy_common.authorize.authorizer import AbstractAuthorizer
from indy_common.constants import TRUST_ANCHOR
from indy_common.test.auth.conftest import IDENTIFIERS
from indy_common.types import Request
from plenum.common.constants import TYPE, TRUSTEE, STEWARD
from plenum.test.helper import randomOperation

PLUGIN_FIELD = "new_field"


class PluginAuthorizer(AbstractAuthorizer):

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraint,
                  auth_action: AbstractAuthAction):
        if not auth_constraint.metadata and PLUGIN_FIELD in request.operation:
            return False, "plugin field must be absent"
        if not auth_constraint.metadata:
            return True, ""
        if PLUGIN_FIELD not in auth_constraint.metadata:
            return True, ""
        if PLUGIN_FIELD not in request.operation:
            return False, "missing required plugin field"

        required_amount = auth_constraint.metadata[PLUGIN_FIELD]
        req_amount = request.operation[PLUGIN_FIELD]

        if req_amount < required_amount:
            return False, "not enough amount in plugin field"

        return True, ""


@pytest.fixture(scope='module')
def write_auth_req_validator(write_auth_req_validator):
    plugin_authorizer = PluginAuthorizer()
    write_auth_req_validator.register_authorizer(plugin_authorizer)
    return write_auth_req_validator


def set_auth_constraint(validator, auth_constraint):
    validator.auth_cons_strategy.get_auth_constraint = lambda a: auth_constraint


def build_req_and_action(role, sig_count, need_to_be_owner, amount=None):
    sig = 'signature' if sig_count == 1 else None
    sigs = {
        **{id: 'signature' for id in IDENTIFIERS[role][:sig_count]},
        **{'id{}'.format(i): 'signature{}'.format(i) for i in range(sig_count - len(IDENTIFIERS[role][:sig_count]))}
    } if sig_count > 1 else None

    operation = randomOperation()
    if amount is not None:
        operation[PLUGIN_FIELD] = amount

    req = Request(identifier=IDENTIFIERS[role][0],
                  operation=operation,
                  signature=sig,
                  signatures=sigs)
    action = AuthActionAdd(txn_type=req.operation[TYPE],
                           field='some_field',
                           value='new_value',
                           is_owner=need_to_be_owner)

    return req, [action]


def build_multisig_req_and_action(roles, need_to_be_owner, amount=None):
    sigs = {IDENTIFIERS[role][i]: 'signature' for role, sig_count in roles.items() for i in range(sig_count)}

    operation = randomOperation()
    if amount is not None:
        operation[PLUGIN_FIELD] = amount

    req = Request(identifier=next(iter(sigs.keys())) if sigs else None,
                  operation=operation,
                  signature=None,
                  signatures=sigs)
    action = AuthActionAdd(txn_type=req.operation[TYPE],
                           field='some_field',
                           value='new_value',
                           is_owner=need_to_be_owner)

    return req, [action]


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (IDENTITY_OWNER, 1, True, 5, True),
    (IDENTITY_OWNER, 1, True, 6, True),
    (IDENTITY_OWNER, 1, True, 1000, True),
    (IDENTITY_OWNER, 2, True, 5, True),
    (IDENTITY_OWNER, 2, True, 6, True),

    (IDENTITY_OWNER, 1, True, 4, False),
    (IDENTITY_OWNER, 1, True, 0, False),
    (IDENTITY_OWNER, 1, True, None, False),
    (IDENTITY_OWNER, 1, False, 5, False),
    (TRUST_ANCHOR, 1, True, 5, False),
    (IDENTITY_OWNER, 0, True, 5, False)
])
def test_plugin_simple_rule_1_sig(write_auth_req_validator, write_request_validation,
                                  role, sig_count, is_owner, amount, result):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 5}))

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (IDENTITY_OWNER, 1, True, 5, True),
    (TRUST_ANCHOR, 1, True, 5, True),
    (STEWARD, 1, True, 5, True),
    (TRUSTEE, 1, True, 5, True),
    (IDENTITY_OWNER, 1, True, 5, True),

    (IDENTITY_OWNER, 1, True, 4, False),
    (TRUST_ANCHOR, 1, True, 4, False),
    (STEWARD, 1, True, 4, False),
    (TRUSTEE, 1, True, 4, False),
    (IDENTITY_OWNER, 1, True, 4, False),

    (IDENTITY_OWNER, 0, True, 5, False),
    (TRUST_ANCHOR, 0, True, 5, False),
    (STEWARD, 0, True, 5, False),
    (TRUSTEE, 0, True, 5, False),
    (IDENTITY_OWNER, 0, True, 5, False),
])
def test_plugin_simple_rule_1_sig_all_roles(write_auth_req_validator, write_request_validation,
                                            role, sig_count, is_owner, amount, result):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role='*', sig_count=1, need_to_be_owner=True,
                                       metadata={PLUGIN_FIELD: 5}))

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (TRUSTEE, 3, False, 5, True),
    (TRUSTEE, 3, True, 5, True),
    (TRUSTEE, 3, False, 6, True),
    (TRUSTEE, 3, False, 10000, True),
    (TRUSTEE, 4, False, 5, True),
    (TRUSTEE, 10, False, 5, True),
    (TRUSTEE, 4, False, 6, True),
    (TRUSTEE, 10, False, 10, True),

    (TRUSTEE, 3, False, 4, False),
    (TRUSTEE, 3, False, 0, False),
    (TRUSTEE, 3, False, None, False),
    (TRUST_ANCHOR, 3, False, 5, False),
    (TRUSTEE, 2, False, 5, False),
    (TRUSTEE, 0, False, 5, False),
])
def test_plugin_simple_rule_3_sig(write_auth_req_validator, write_request_validation,
                                  role, sig_count, is_owner, amount, result):
    set_auth_constraint(write_auth_req_validator,
                        AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False,
                                       metadata={PLUGIN_FIELD: 5}))

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (TRUSTEE, 1, False, 5, True),
    (TRUSTEE, 1, False, 6, True),
    (TRUSTEE, 1, False, 10, True),
    (TRUSTEE, 1, False, 15, True),
    (TRUSTEE, 2, False, 5, True),
    (TRUSTEE, 1, True, 5, True),
    (TRUSTEE, 10, True, 15, True),

    (STEWARD, 1, False, 10, True),
    (STEWARD, 1, False, 11, True),
    (STEWARD, 1, False, 15, True),
    (STEWARD, 2, False, 10, True),
    (STEWARD, 1, True, 10, True),
    (STEWARD, 10, True, 15, True),

    (TRUST_ANCHOR, 1, False, 15, True),
    (TRUST_ANCHOR, 1, False, 16, True),
    (TRUST_ANCHOR, 1, False, 20, True),
    (TRUST_ANCHOR, 2, False, 15, True),
    (TRUST_ANCHOR, 1, True, 15, True),
    (TRUST_ANCHOR, 10, True, 20, True),

    (TRUSTEE, 1, False, 4, False),
    (TRUSTEE, 1, False, 0, False),
    (TRUSTEE, 1, False, None, False),

    (STEWARD, 1, False, 9, False),
    (STEWARD, 1, False, 0, False),
    (STEWARD, 1, False, None, False),

    (TRUST_ANCHOR, 1, False, 11, False),
    (TRUST_ANCHOR, 1, False, 0, False),
    (TRUST_ANCHOR, 1, False, None, False),

    (IDENTITY_OWNER, 1, False, 5, False),
    (IDENTITY_OWNER, 1, False, 10, False),
    (IDENTITY_OWNER, 1, False, 15, False),
    (IDENTITY_OWNER, 1, False, 10000, False),

    (TRUSTEE, 0, False, 5, False),
    (STEWARD, 0, False, 10, False),
    (TRUST_ANCHOR, 0, False, 15, False),
    (IDENTITY_OWNER, 0, False, 10000, False),
])
def test_plugin_or_rule_all_amount(write_auth_req_validator, write_request_validation,
                                   role, sig_count, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 5}),
        AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10}),
        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 15}),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (TRUST_ANCHOR, 1, False, 10, True),
    (TRUST_ANCHOR, 2, False, 10, True),
    (TRUST_ANCHOR, 1, True, 15, True),
    (TRUST_ANCHOR, 1, False, None, True),

    (TRUST_ANCHOR, 1, False, 9, False),
    (TRUST_ANCHOR, 1, False, 0, False),
    (TRUST_ANCHOR, 0, False, 10, False),

    (TRUSTEE, 1, False, 10, False),
    (STEWARD, 1, False, 10, False),
    (IDENTITY_OWNER, 1, False, 10, False),

])
def test_plugin_or_rule_one_amount_same_role(write_auth_req_validator, write_request_validation,
                                             role, sig_count, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False),
        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10}),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (TRUST_ANCHOR, 1, False, None, True),
    (TRUST_ANCHOR, 2, True, None, True),
    (IDENTITY_OWNER, 1, False, 10, True),
    (IDENTITY_OWNER, 2, False, 10, True),
    (IDENTITY_OWNER, 1, False, 11, True),

    (TRUST_ANCHOR, 1, False, 10, False),
    (TRUST_ANCHOR, 1, False, 9, False),
    (TRUST_ANCHOR, 1, False, 0, False),
    (TRUST_ANCHOR, 0, False, 10, False),
    (TRUST_ANCHOR, 0, False, None, False),

    (IDENTITY_OWNER, 1, False, 9, False),
    (IDENTITY_OWNER, 1, False, 0, False),
    (IDENTITY_OWNER, 1, False, None, False),
    (IDENTITY_OWNER, 0, False, 10, False),

    (TRUSTEE, 1, False, 10, False),
    (STEWARD, 1, False, 10, False),
    (TRUSTEE, 1, False, None, False),
    (STEWARD, 1, False, None, False),

])
def test_plugin_or_rule_one_amount_diff_roles(write_auth_req_validator, write_request_validation,
                                              role, sig_count, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False),
        AuthConstraint(role=IDENTITY_OWNER, sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10}),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('role, sig_count, is_owner, amount, result', [
    (TRUST_ANCHOR, 1, False, None, True),
    (TRUST_ANCHOR, 2, True, None, True),
    (TRUST_ANCHOR, 1, False, 10, True),
    (TRUST_ANCHOR, 2, False, 10, True),
    (TRUST_ANCHOR, 1, False, 11, True),
    (IDENTITY_OWNER, 1, False, 10, True),
    (IDENTITY_OWNER, 2, False, 10, True),
    (IDENTITY_OWNER, 1, False, 11, True),
    (STEWARD, 1, False, 10, True),
    (STEWARD, 2, False, 10, True),
    (STEWARD, 1, False, 11, True),
    (TRUSTEE, 1, False, 10, True),
    (TRUSTEE, 2, False, 10, True),
    (TRUSTEE, 1, False, 11, True),

    (TRUST_ANCHOR, 1, False, 9, False),
    (TRUST_ANCHOR, 1, False, 0, False),
    (TRUST_ANCHOR, 0, False, 10, False),
    (TRUST_ANCHOR, 0, False, None, False),

    (IDENTITY_OWNER, 1, False, 9, False),
    (IDENTITY_OWNER, 1, False, 0, False),
    (IDENTITY_OWNER, 1, False, None, False),
    (IDENTITY_OWNER, 0, False, 10, False),
    (STEWARD, 1, False, 9, False),
    (STEWARD, 1, False, 0, False),
    (STEWARD, 1, False, None, False),
    (STEWARD, 0, False, 10, False),
    (TRUSTEE, 1, False, 9, False),
    (TRUSTEE, 1, False, 0, False),
    (TRUSTEE, 1, False, None, False),
    (TRUSTEE, 0, False, 10, False),

])
def test_plugin_or_rule_one_amount_all_roles(write_auth_req_validator, write_request_validation,
                                             role, sig_count, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraint(role=TRUST_ANCHOR, sig_count=1, need_to_be_owner=False),
        AuthConstraint(role='*', sig_count=1, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10}),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_req_and_action(role, sig_count, is_owner, amount)) == result


@pytest.mark.parametrize('roles, is_owner, amount, result', [
    ({TRUSTEE: 2, STEWARD: 3}, False, 10, True),
    ({TRUSTEE: 3, STEWARD: 3}, False, 10, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, 10, True),
    ({TRUSTEE: 3, STEWARD: 4}, False, 10, True),
    ({TRUSTEE: 3, STEWARD: 4}, False, 11, True),

    ({TRUSTEE: 1, STEWARD: 3}, False, 10, False),
    ({TRUSTEE: 2, STEWARD: 2}, False, 10, False),

    ({TRUSTEE: 2, STEWARD: 3}, False, 9, False),
    ({TRUSTEE: 2, STEWARD: 3}, False, 0, False),
    ({TRUSTEE: 2, STEWARD: 3}, False, None, False),

    ({TRUSTEE: 2}, False, 10, False),
    ({TRUSTEE: 2}, False, None, False),
    ({TRUSTEE: 3}, False, 10, False),
    ({STEWARD: 3}, False, 10, False),
    ({STEWARD: 4}, False, 10, False),
    ({}, False, 10, False),

    ({IDENTITY_OWNER: 2, STEWARD: 3}, False, 10, False),
    ({IDENTITY_OWNER: 2, TRUSTEE: 3}, False, 10, False),

])
def test_plugin_and_rule(write_auth_req_validator, write_request_validation,
                         roles, is_owner, amount, result):
    auth_constr = AuthConstraintAnd(auth_constraints=[
        AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10}),
        AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False,
                       metadata={PLUGIN_FIELD: 10})
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_multisig_req_and_action(roles, is_owner, amount)) == result


@pytest.mark.parametrize('roles, is_owner, amount, result', [
    ({TRUSTEE: 2, STEWARD: 3}, False, 10, True),
    ({TRUSTEE: 3, STEWARD: 3}, False, 10, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, 10, True),
    ({TRUSTEE: 3, STEWARD: 4}, False, 10, True),

    ({TRUSTEE: 2, STEWARD: 3}, False, 15, True),
    ({TRUSTEE: 3, STEWARD: 3}, False, 15, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, 15, True),
    ({TRUSTEE: 3, STEWARD: 4}, False, 15, True),

    ({TRUSTEE: 2, STEWARD: 3}, False, None, True),
    ({TRUSTEE: 3, STEWARD: 3}, False, None, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, None, True),
    ({TRUSTEE: 3, STEWARD: 4}, False, None, True),

    ({TRUSTEE: 1, STEWARD: 3}, False, 10, False),
    ({TRUSTEE: 2, STEWARD: 2}, False, 10, False),

    ({TRUSTEE: 2, STEWARD: 3}, False, 9, False),
    ({TRUSTEE: 2, STEWARD: 3}, False, 0, False),

    ({TRUSTEE: 2}, False, 10, False),
    ({TRUSTEE: 2}, False, None, False),
    ({TRUSTEE: 3}, False, 10, False),
    ({STEWARD: 3}, False, 15, False),
    ({STEWARD: 4}, False, 15, False),
    ({}, False, 100, False),

    ({IDENTITY_OWNER: 2, STEWARD: 3}, False, 15, False),
    ({IDENTITY_OWNER: 2, TRUSTEE: 3}, False, 10, False),

])
def test_plugin_and_or_rule_same_role(write_auth_req_validator, write_request_validation,
                                      roles, is_owner, amount, result):
    auth_constr = AuthConstraintAnd(auth_constraints=[
        AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False),
            AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
        ]),
        AuthConstraintOr(auth_constraints=[
            AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False),
            AuthConstraint(role=STEWARD, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
        ])
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_multisig_req_and_action(roles, is_owner, amount)) == result


@pytest.mark.parametrize('roles, is_owner, amount, result', [
    # 1st
    ({TRUSTEE: 3}, False, None, True),
    ({TRUSTEE: 4}, False, None, True),

    ({TRUSTEE: 2}, False, None, False),
    ({TRUSTEE: 3}, False, 1000, False),

    # 2d
    ({TRUSTEE: 1, STEWARD: 2}, False, None, True),
    ({TRUSTEE: 2, STEWARD: 2}, False, None, True),
    ({TRUSTEE: 1, STEWARD: 3}, False, None, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, None, True),

    ({TRUSTEE: 1, STEWARD: 2}, False, 1000, False),
    ({TRUSTEE: 2, STEWARD: 2}, False, 1000, False),
    ({TRUSTEE: 1, STEWARD: 3}, False, 1000, False),
    ({TRUSTEE: 2, STEWARD: 4}, False, 1000, False),

    ({STEWARD: 2}, False, None, False),
    ({STEWARD: 4}, False, None, False),

    # 3d
    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 10, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 10, True),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 10, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 10, True),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 15, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 15, True),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 15, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 15, True),

    ({TRUSTEE: 1, TRUST_ANCHOR: 1}, False, 10, False),
    ({TRUST_ANCHOR: 3}, False, 10, False),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, None, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, None, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, None, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, None, False),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 9, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 9, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 9, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 9, False),

    # 4th
    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, 15, True),
    ({TRUSTEE: 3, IDENTITY_OWNER: 3}, False, 15, True),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, 15, True),
    ({TRUSTEE: 3, IDENTITY_OWNER: 4}, False, 15, True),

    ({TRUSTEE: 1, IDENTITY_OWNER: 3}, False, 15, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 2}, False, 15, False),
    ({IDENTITY_OWNER: 4}, False, 15, False),

    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, 14, False),
    ({TRUSTEE: 3, IDENTITY_OWNER: 3}, False, 14, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, 14, False),
    ({TRUSTEE: 3, IDENTITY_OWNER: 4}, False, 14, False),

    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, None, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, None, False),

    # other
    ({TRUSTEE: 1, TRUST_ANCHOR: 1, STEWARD: 1, IDENTITY_OWNER: 1}, False, 100, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 1, STEWARD: 1, IDENTITY_OWNER: 1}, False, None, False),

])
def test_plugin_or_and_rule_diff_roles(write_auth_req_validator, write_request_validation,
                                       roles, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
            AuthConstraint(role=TRUST_ANCHOR, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 15}),
            AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 15}),
        ]),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_multisig_req_and_action(roles, is_owner, amount)) == result


@pytest.mark.parametrize('roles, is_owner, amount, result', [
    # 1st
    ({TRUSTEE: 3}, False, None, True),
    ({TRUSTEE: 4}, False, None, True),

    ({TRUSTEE: 2}, False, None, False),
    ({TRUSTEE: 3}, False, 1000, False),

    # 2d
    ({TRUSTEE: 1, STEWARD: 2}, False, None, True),
    ({TRUSTEE: 2, STEWARD: 2}, False, None, True),
    ({TRUSTEE: 1, STEWARD: 3}, False, None, True),
    ({TRUSTEE: 2, STEWARD: 4}, False, None, True),

    ({TRUSTEE: 1, STEWARD: 2}, False, 1000, False),
    ({TRUSTEE: 2, STEWARD: 2}, False, 1000, False),
    ({TRUSTEE: 1, STEWARD: 3}, False, 1000, False),
    ({TRUSTEE: 2, STEWARD: 4}, False, 1000, False),

    ({STEWARD: 2}, False, None, False),
    ({STEWARD: 4}, False, None, False),

    # 3d
    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 10, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 10, True),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 10, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 10, True),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 15, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 15, True),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 15, True),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 15, True),

    ({TRUSTEE: 1, TRUST_ANCHOR: 1}, False, 10, False),
    ({TRUST_ANCHOR: 3}, False, 10, False),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, None, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, None, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, None, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, None, False),

    ({TRUSTEE: 1, TRUST_ANCHOR: 2}, False, 9, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 2}, False, 9, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 3}, False, 9, False),
    ({TRUSTEE: 2, TRUST_ANCHOR: 4}, False, 9, False),

    # 4th
    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, 15, True),
    ({TRUSTEE: 3, IDENTITY_OWNER: 3}, False, 15, True),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, 15, True),
    ({TRUSTEE: 3, IDENTITY_OWNER: 4}, False, 15, True),

    ({TRUSTEE: 1, IDENTITY_OWNER: 3}, False, 15, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 2}, False, 15, False),
    ({IDENTITY_OWNER: 4}, False, 15, False),

    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, 14, False),
    ({TRUSTEE: 3, IDENTITY_OWNER: 3}, False, 14, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, 14, False),
    ({TRUSTEE: 3, IDENTITY_OWNER: 4}, False, 14, False),

    ({TRUSTEE: 2, IDENTITY_OWNER: 3}, False, None, False),
    ({TRUSTEE: 2, IDENTITY_OWNER: 4}, False, None, False),

    # other
    ({TRUSTEE: 1, TRUST_ANCHOR: 1, STEWARD: 1, IDENTITY_OWNER: 1}, False, 100, False),
    ({TRUSTEE: 1, TRUST_ANCHOR: 1, STEWARD: 1, IDENTITY_OWNER: 1}, False, None, False),

])
def test_plugin_complex(write_auth_req_validator, write_request_validation,
                        roles, is_owner, amount, result):
    auth_constr = AuthConstraintOr(auth_constraints=[
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=3, need_to_be_owner=False),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False),
            AuthConstraint(role=STEWARD, sig_count=2, need_to_be_owner=False),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=1, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
            AuthConstraint(role=TRUST_ANCHOR, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 10}),
        ]),
        AuthConstraintAnd(auth_constraints=[
            AuthConstraint(role=TRUSTEE, sig_count=2, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 15}),
            AuthConstraint(role=IDENTITY_OWNER, sig_count=3, need_to_be_owner=False,
                           metadata={PLUGIN_FIELD: 15}),
        ]),
    ])
    set_auth_constraint(write_auth_req_validator, auth_constr)

    assert write_request_validation(*build_multisig_req_and_action(roles, is_owner, amount)) == result
