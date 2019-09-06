from abc import ABCMeta
from logging import getLogger

import os

from indy_common.authorize.auth_actions import AbstractAuthAction
from indy_common.authorize.auth_constraints import AbstractAuthConstraint, AuthConstraint, \
    AuthConstraintAnd, ConstraintsEnum, AuthConstraintOr, AuthConstraintForbidden
from indy_common.authorize.helper import get_named_role
from indy_common.constants import ENDORSER, ENDORSER_STRING
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import STEWARD, TRUSTEE, TRUSTEE_STRING, STEWARD_STRING

logger = getLogger()


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
                  auth_action: AbstractAuthAction) -> (bool, str):
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
        if idr is None:
            return None
        return self._get_role(idr)

    def get_sig_count(self, request: Request, role: str = "*", off_ledger_signature=False):
        if request.signature:
            return 1 \
                if off_ledger_signature or self.is_role_accepted(self._get_role(request.identifier), role) \
                else 0
        elif not request.signatures:
            return 0
        if role == "*":
            return len(request.signatures)

        sig_count = 0
        for identifier, _ in request.signatures.items():
            signer_role = self._get_role(identifier)
            if off_ledger_signature or self.is_role_accepted(signer_role, role):
                sig_count += 1
        return sig_count

    def is_owner_accepted(self, constraint: AuthConstraint, action: AbstractAuthAction):
        if constraint.need_to_be_owner and not action.is_owner:
            return False
        return True

    def is_role_accepted(self, role, auth_constraint_role):
        # The field 'role' contains a value from the cache.
        # None - the identifier doesn't found in the cache.
        # "" - IDENTITY_OWNER
        # The field 'auth_constraint_role' contains a role from the auth_map
        # None - IDENTITY_OWNER
        if role is None:
            return False
        if role == "":
            role = None
        return role == auth_constraint_role or auth_constraint_role == '*'

    def is_sig_count_accepted(self, request: Request, auth_constraint: AuthConstraint):
        role = auth_constraint.role
        sig_count = self.get_sig_count(request, role=role, off_ledger_signature=auth_constraint.off_ledger_signature)
        return sig_count >= auth_constraint.sig_count

    def get_named_role_from_req(self, request: Request):
        return get_named_role(self.get_role(request))

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraint,
                  auth_action: AbstractAuthAction = None):
        # 1. Check that the Author is the owner
        # do first since it doesn't require going to state
        if not self.is_owner_accepted(auth_constraint, auth_action):
            if auth_action.field != '*':
                return False, "{} can not touch {} field since only the owner can modify it". \
                    format(self.get_named_role_from_req(request),
                           auth_action.field)
            else:
                return False, "{} can not edit {} txn since only owner can modify it". \
                    format(self.get_named_role_from_req(request),
                           IndyTransactions.get_name_from_code(auth_action.txn_type))

        author_role = self.get_role(request)

        # 2. Check that the Author is present on the ledger
        if auth_constraint.sig_count > 0 and not auth_constraint.off_ledger_signature and author_role is None:
            return False, "sender's DID {} is not found in the Ledger".format(request.identifier)

        # 3. Check that the Author signed the transaction in case of multi-sig
        if auth_constraint.sig_count > 0 and request.signatures and request.identifier not in request.signatures:
            return False, "Author must sign the transaction"

        # 4. Check that there are enough signatures of the needed role
        if not self.is_sig_count_accepted(request, auth_constraint):
            role = Roles(auth_constraint.role).name if auth_constraint.role != '*' else '*'
            return False, "Not enough {} signatures".format(role)

        return True, ""

    def _get_role(self, idr):
        try:
            return self.cache.getRole(idr, isCommitted=False)
        except KeyError:
            return None


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
                  auth_constraint: AuthConstraintOr,
                  auth_action: AbstractAuthAction):
        successes = []
        fails = []
        for constraint in auth_constraint.auth_constraints:
            try:
                self.parent.authorize(request=request,
                                      auth_constraint=constraint,
                                      auth_action=auth_action)
            except AuthValidationError as e:
                logger.trace(e)
                fails.append("Constraint: {}, Error: {}".format(constraint, e.reason))
            else:
                successes.append(True)
        if len(successes) == 0:
            raise AuthValidationError(
                os.linesep.join(["Rule for this action is: {}".format(auth_constraint),
                                 "Failed checks:",
                                 os.linesep.join(fails)])
            )
        return True, ""


class ForbiddenAuthorizer(AbstractAuthorizer):

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraintForbidden,
                  auth_action: AbstractAuthAction):
        return False, str(auth_constraint)


class EndorserAuthorizer(AbstractAuthorizer):
    NO_NEED_FOR_ENDORSER_ROLES = {ENDORSER, TRUSTEE, STEWARD}
    NO_NEED_FOR_ENDORSER_ROLES_STR = [ENDORSER_STRING, TRUSTEE_STRING, STEWARD_STRING]

    ENDORSER_ROLES = {ENDORSER}
    ENDORSER_ROLES_STR = {ENDORSER_STRING}

    def __init__(self, cache: IdrCache):
        super().__init__()
        self.cache = cache

    def authorize(self,
                  request: Request,
                  auth_constraint: AuthConstraint,
                  auth_action: AbstractAuthAction = None):
        # check if endorser role is valid first
        res, reason = self._check_endorser_role(request)
        if not res:
            return res, reason

        # check if Endorser field must be explicitly present
        res, reason = self._check_endorser_field_presence(request)
        if not res:
            return res, reason

        return True, ""

    def _check_endorser_role(self, request):
        if request.endorser is None:
            return True, ""

        endorser_role = self._get_role(request.endorser)
        if endorser_role not in self.ENDORSER_ROLES:
            return False, "Endorser must have one of the following roles: {}".format(str(self.ENDORSER_ROLES_STR))

        return True, ""

    def _check_endorser_field_presence(self, request):
        # 1. Check that if Endorser is present, Endorser must sign the transaction
        # if author=endorser, then no multi-sig is required, since he's already signed the txn
        if request.endorser != request.identifier:
            if request.endorser and not request.signatures:
                return False, "Endorser must sign the transaction"
            if request.endorser and request.endorser not in request.signatures:
                return False, "Endorser must sign the transaction"

        # 2. Endorser is required only when the transaction is endorsed, that is signed by someone else besides the author.
        # If the auth rule requires an endorser to submit the transaction, then it will be caught by the Roles Authorizer,
        # so no need to check anything here if we don't have any extra signatures.
        if not request.signatures:
            return True, ""
        has_extra_sigs = len(request.signatures) > 1 or (request.identifier not in request.signatures)
        if not has_extra_sigs:
            return True, ""

        # 3. Endorser is required for unprivileged roles only
        author_role = self._get_role(request.identifier)
        if author_role == "":  # "" - IDENTITY_OWNER
            author_role = None
        if author_role in self.NO_NEED_FOR_ENDORSER_ROLES:
            return True, ""

        # 4. Endorser field is not required when multi-signed by non-privileged roles only
        has_privileged_sig = False
        for idr, _ in request.signatures.items():
            role = self._get_role(idr)
            if role in self.NO_NEED_FOR_ENDORSER_ROLES:
                has_privileged_sig = True
                break
        if not has_privileged_sig:
            return True, ""

        # 5. Check that Endorser field is present
        if request.endorser is None:
            return False, "'Endorser' field must be explicitly set for the endorsed transaction"

        return True, ""

    def _get_role(self, idr):
        if idr is None:
            return None
        try:
            return self.cache.getRole(idr, isCommitted=False)
        except KeyError:
            return None
