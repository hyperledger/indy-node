from abc import ABCMeta

from indy_common.auth_constraints import AuthConstraint, AbstractAuthConstraint, ROLE_CONSTRAINT_ID, AuthConstraintAnd
from indy_common.auth_actions import AbstractAuthAction
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import TXN_TYPE, NYM, TARGET_NYM


class AuthRuleNotFound(Exception):
    pass


class AuthValidationError(Exception):
    pass


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
        """Also need to check isOwner or not"""
        idr = request.identifier
        try:
            role = self.cache.getRole(idr, isCommitted=False)
        except KeyError:
            role = None

        return role

    def get_sig_count(self, request: Request):
        pass

    def _get_req_owner_for_nym(self, request: Request):
        try:
            owner = self.cache.getOwnerFor(request.identifier, isCommitted=False)
        except KeyError:
            """Not found in idrCache"""
            owner = None
        return owner

    def _get_txn_owner_for_nym(self, request: Request):
        try:
            owner = self.cache.getOwnerFor(request.operation[TARGET_NYM], isCommitted=False)
        except KeyError:
            """Not found in idrCache"""
            owner = None
        return owner

    def _get_req_owner(self, request: Request):
        return request.identifier

    def _get_txn_owner(self, request: Request):
        txn_type = request.operation[TXN_TYPE]
        if txn_type == NYM:
            return self._get_txn_owner_for_nym(request)
        return None

    def is_owner_accepted(self, request: Request, constraint: AuthConstraint):
        if constraint.need_to_be_owner and \
                self._get_req_owner(request) != self._get_txn_owner(request):
            return False
        return True

    def is_role_accepted(self, request: Request, auth_constraint: AuthConstraint):
        role = self.get_role(request)
        if role:
            return role == auth_constraint.role or auth_constraint.role == '*'

    def is_sig_count_accepted(self, request: Request, auth_constraint: AuthConstraint):
        sig_count = 1
        if auth_constraint.sig_count != 1:
            sig_count = self.get_sig_count(request)

        return sig_count >= auth_constraint.sig_count

    def authorize(self, request: Request, auth_constraint: AuthConstraint, auth_action: AbstractAuthAction=None):
        if not self.is_role_accepted(request, auth_constraint):
            return False, "role is not accepted"
        if not self.is_sig_count_accepted(request, auth_constraint):
            return False, "count of signatures is not accepted"
        if not self.is_owner_accepted(request, auth_constraint):
            return False, "actor must be owner"
        return True, ""


class CompositeAuthorizer(AbstractAuthorizer):
    def __init__(self):
        super().__init__()
        self.authorizers = {}

    def register_authorizer(self, authorizer, auth_constraint_id=ROLE_CONSTRAINT_ID):
        authorizer.parent = self
        self.authorizers.setdefault(auth_constraint_id, []).append(authorizer)

    def authorize(self, request: Request, auth_constraint: AuthConstraint, auth_action: AbstractAuthAction):
        for authorizer in self.authorizers.get(auth_constraint.constraint_id):
            authorized, reason = authorizer.authorize(request=request,
                                                      auth_constraint=auth_constraint,
                                                      auth_action=auth_action)
            if not authorized:
                raise AuthValidationError("Validation error with reason: {}".format(reason))
            return True, ""


class AndAuthorizer(CompositeAuthorizer):

    def authorize(self, request, auth_constraint: AuthConstraintAnd, auth_action: AbstractAuthAction):
        for constraint in auth_constraint.auth_constraints:
            authorized, reason = self.parent.authorize(request=request,
                                                       auth_constraint=constraint,
                                                       auth_action=auth_action)
            if not authorized:
                raise AuthValidationError("Validation error with reason: {}".format(reason))
        return True, ""


class OrAuthorizer(CompositeAuthorizer):

    def authorize(self, request, auth_constraint: AuthConstraintAnd, auth_action: AbstractAuthAction):
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
            raise AuthValidationError("There is no accepted constraint")
        return True, ""
