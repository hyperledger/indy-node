from abc import ABCMeta

from indy_common.authorize.auth_actions import AbstractAuthAction
from indy_common.authorize.auth_constraints import AbstractAuthConstraint, AuthConstraint, \
    AuthConstraintAnd, ConstraintsEnum
from indy_common.authorize.helper import get_named_role
from indy_common.constants import NYM, CLAIM_DEF
from indy_common.transactions import IndyTransactions
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache


class AuthValidationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Validation error with reason: {}".format(self.reason)


class AbstractAuthorizer(metaclass=ABCMeta):

    def __init__(self):
        self.parent = None

    def authorize(self,
                  request: Request,
                  auth_constraint: AbstractAuthConstraint,
                  auth_action: AbstractAuthAction)-> (bool, str):
        raise NotImplementedError()


class RolesAuthorizer(AbstractAuthorizer):
    def __init__(self, cache: IdrCache):
        super().__init__()
        self.cache = cache

    def get_role(self, request: Request):
        """
        None roles are stored as empty strings, so the role returned as None
        by this function means that corresponding DID is not stored in a ledger.
        """
        idr = request.identifier
        try:
            role = self.cache.getRole(idr, isCommitted=False)
        except KeyError:
            role = None

        return role

    def get_sig_count(self, request: Request):
        pass

    def is_owner_accepted(self, constraint: AuthConstraint, action: AbstractAuthAction):
        if constraint.need_to_be_owner and not action.is_owner:
            return False
        return True

    def is_role_accepted(self, request: Request, auth_constraint: AuthConstraint):
        role = self.get_role(request)
        return role == auth_constraint.role or auth_constraint.role == '*' \
            if role is not None else None

    def is_sig_count_accepted(self, request: Request, auth_constraint: AuthConstraint):
        sig_count = 1
        if auth_constraint.sig_count != 1:
            sig_count = self.get_sig_count(request)

        return sig_count >= auth_constraint.sig_count

    def get_named_role_from_req(self, request: Request):
        return get_named_role(self.get_role(request))

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraint,
                  auth_action: AbstractAuthAction=None):
        is_role_accepted = self.is_role_accepted(request, auth_constraint)
        if is_role_accepted is None:
            return False, "sender's DID {} is not found in the Ledger".format(request.identifier)
        if not is_role_accepted:
            return False, "{} can not do this action".format(self.get_named_role_from_req(request))
        if not self.is_sig_count_accepted(request, auth_constraint):
            return False, "Not enough signatures"
        if not self.is_owner_accepted(auth_constraint, auth_action):
            if auth_action.field != '*':
                return False, "{} can not touch {} field since only the owner can modify it".\
                    format(self.get_named_role_from_req(request),
                           auth_action.field)
            else:
                return False, "{} can not edit {} txn since only owner can modify it".\
                    format(self.get_named_role_from_req(request),
                           IndyTransactions.get_name_from_code(auth_action.txn_type))
        return True, ""


class CompositeAuthorizer(AbstractAuthorizer):
    def __init__(self):
        super().__init__()
        self.authorizers = {}

    def register_authorizer(self, authorizer, auth_constraint_id=ConstraintsEnum.ROLE_CONSTRAINT_ID):
        authorizer.parent = self
        self.authorizers.setdefault(auth_constraint_id, []).append(authorizer)

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraint,
                  auth_action: AbstractAuthAction):
        for authorizer in self.authorizers.get(auth_constraint.constraint_id):
            authorized, reason = authorizer.authorize(request=request,
                                                      auth_constraint=auth_constraint,
                                                      auth_action=auth_action)
            if not authorized:
                raise AuthValidationError(reason)
            return True, ""


class AndAuthorizer(AbstractAuthorizer):

    def authorize(self,
                  request,
                  auth_constraint: AuthConstraintAnd,
                  auth_action: AbstractAuthAction):
        for constraint in auth_constraint.auth_constraints:
            authorized, reason = self.parent.authorize(request=request,
                                                       auth_constraint=constraint,
                                                       auth_action=auth_action)
            if not authorized:
                raise AuthValidationError(reason)
        return True, ""


class OrAuthorizer(AbstractAuthorizer):

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraintAnd,
                  auth_action: AbstractAuthAction):
        successes = []
        for constraint in auth_constraint.auth_constraints:
            try:
                self.parent.authorize(request=request,
                                      auth_constraint=constraint,
                                      auth_action=auth_action)
            except AuthValidationError:
                pass
            else:
                successes.append(True)
        if len(successes) == 0:
            raise AuthValidationError("Rule for this action is: {}".format(auth_constraint))
        return True, ""
