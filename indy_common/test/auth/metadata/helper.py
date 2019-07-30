import pytest

from indy_common.authorize.auth_actions import AbstractAuthAction, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize.authorizer import AbstractAuthorizer
from indy_common.test.constants import IDENTIFIERS
from indy_common.types import Request
from plenum.common.constants import TYPE
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

        if req_amount != required_amount:
            return False, "not enough amount in plugin field"

        return True, ""


def set_auth_constraint(validator, auth_constraint):
    validator.auth_cons_strategy.get_auth_constraint = lambda a: auth_constraint


def build_req_and_action(signatures, need_to_be_owner, amount=None):
    sig = None
    sigs = None
    identifier = None

    if signatures:
        role = next(iter(signatures.keys()))
        identifier = IDENTIFIERS[role][0]

    if len(signatures) == 1 and next(iter(signatures.values())) == 1:
        sig = 'signature'
    else:
        sigs = {IDENTIFIERS[role][i]: 'signature' for role, sig_count in signatures.items() for i in range(sig_count)}

    operation = randomOperation()
    if amount is not None:
        operation[PLUGIN_FIELD] = amount

    req = Request(identifier=identifier,
                  operation=operation,
                  signature=sig,
                  signatures=sigs)
    action = AuthActionAdd(txn_type=req.operation[TYPE],
                           field='some_field',
                           value='new_value',
                           is_owner=need_to_be_owner)

    return req, [action]


def validate(auth_constraint,
             valid_actions,
             all_signatures, is_owner, amount,
             write_auth_req_validator,
             write_request_validation):
    set_auth_constraint(write_auth_req_validator,
                        auth_constraint)

    for signatures in all_signatures:
        next_action = (signatures, is_owner, amount)
        expected = is_expected(next_action, valid_actions)
        result = write_request_validation(*build_req_and_action(*next_action))
        assert result == expected, \
            "Expected {} but result is {} for case {} and valid set {}".format(expected, result, next_action,
                                                                               valid_actions)


def is_expected(next_action, valid_actions):
    for valid_action in valid_actions:
        if next_action[1] != valid_action[1]:  # owner
            continue
        if next_action[2] != valid_action[2]:  # amount
            continue
        valid_signatures = valid_action[0]
        next_action_signatures = next_action[0]
        if valid_signatures.items() <= next_action_signatures.items():  # we may have more signatures than required, this is fine
            return True
    return False
