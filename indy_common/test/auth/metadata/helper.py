from typing import NamedTuple, List, Optional

from indy_common.authorize.auth_actions import AbstractAuthAction, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize.authorizer import AbstractAuthorizer
from indy_common.test.constants import IDENTIFIERS
from indy_common.types import Request
from plenum.common.constants import TYPE
from plenum.test.helper import randomOperation

PLUGIN_FIELD = "new_field"

Action = NamedTuple('Action',
                    [("author", str), ("endorser", Optional[str]), ("sigs", dict),
                     ("is_owner", bool), ("amount", int), ("extra_sigs", bool)])


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


def build_req_and_action(action: Action):
    sig = None
    sigs = None
    identifier = IDENTIFIERS[action.author][0]
    endorser_did = None

    # if there is only 1 sig from the Author - use `signature` instead of `signatures`
    if len(action.sigs) == 1 and next(iter(action.sigs.values())) == 1 and next(
            iter(action.sigs.keys())) == action.author:
        sig = 'signature'
    else:
        sigs = {IDENTIFIERS[role][i]: 'signature' for role, sig_count in action.sigs.items() for i in
                range(sig_count)}

    if action.endorser is not None:
        endorser_did = IDENTIFIERS[action.endorser][0]

    operation = randomOperation()
    if action.amount is not None:
        operation[PLUGIN_FIELD] = action.amount

    req = Request(identifier=identifier,
                  operation=operation,
                  signature=sig,
                  signatures=sigs,
                  endorser=endorser_did)
    action = AuthActionAdd(txn_type=req.operation[TYPE],
                           field='some_field',
                           value='new_value',
                           is_owner=action.is_owner)

    return req, [action]


def validate(auth_constraint,
             valid_actions: List[Action],
             author, endorser, all_signatures, is_owner, amount,
             write_auth_req_validator,
             write_request_validation):
    set_auth_constraint(write_auth_req_validator,
                        auth_constraint)

    for signatures in all_signatures:
        next_action = Action(author=author, endorser=endorser, sigs=signatures,
                             is_owner=is_owner, amount=amount, extra_sigs=False)
        expected = is_expected(next_action, valid_actions)
        result = write_request_validation(*build_req_and_action(next_action))
        assert result == expected, \
            "Expected {} but result is {} for case {} and valid set {}".format(expected, result, next_action,
                                                                               valid_actions)


def is_expected(next_action: Action, valid_actions: List[Action]):
    for valid_action in valid_actions:
        if (next_action.author, next_action.endorser, next_action.is_owner, next_action.amount) != \
                (valid_action.author, valid_action.endorser, valid_action.is_owner, valid_action.amount):
            continue
        if not valid_action.extra_sigs and next_action.sigs != valid_action.sigs:
            continue
        if valid_action.extra_sigs and not (valid_action.sigs.items() <= next_action.sigs.items()):
            continue
        return True
    return False
