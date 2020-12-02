from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List
from indy_common.authorize.helper import get_named_role
from indy_common.constants import NETWORK_MONITOR, ENDORSER
from plenum.common.constants import STEWARD, TRUSTEE

CONSTRAINT_ID = "constraint_id"
AUTH_CONSTRAINTS = "auth_constraints"
ROLE = "role"
METADATA = "metadata"
SIG_COUNT = "sig_count"
NEED_TO_BE_OWNER = "need_to_be_owner"
OFF_LEDGER_SIGNATURE = "off_ledger_signature"

IDENTITY_OWNER = None

accepted_roles = [IDENTITY_OWNER, NETWORK_MONITOR, ENDORSER, STEWARD, TRUSTEE, '*']


class ConstraintEnum(Enum):
    def __str__(self):
        return self.name


class ConstraintsEnum:
    ROLE_CONSTRAINT_ID = 'ROLE'
    AND_CONSTRAINT_ID = 'AND'
    OR_CONSTRAINT_ID = 'OR'
    FORBIDDEN_CONSTRAINT_ID = 'FORBIDDEN'

    @staticmethod
    def values():
        return [ConstraintsEnum.ROLE_CONSTRAINT_ID,
                ConstraintsEnum.AND_CONSTRAINT_ID,
                ConstraintsEnum.OR_CONSTRAINT_ID,
                ConstraintsEnum.FORBIDDEN_CONSTRAINT_ID]


class AbstractAuthConstraint(metaclass=ABCMeta):
    def __init__(self):
        self.constraint_id = ''

    @property
    def as_dict(self):
        raise NotImplementedError()

    def __str__(self):
        return str(self)

    def __eq__(self, other):
        if self.as_dict != other.as_dict:
            return False
        return True

    def set_metadata(self, metadata: dict):
        raise NotImplementedError()

    @staticmethod
    def from_dict(as_dict):
        raise NotImplementedError()


class AuthConstraintForbidden(AbstractAuthConstraint):

    def __init__(self):
        self.constraint_id = ConstraintsEnum.FORBIDDEN_CONSTRAINT_ID

    @property
    def as_dict(self):
        return {CONSTRAINT_ID: self.constraint_id}

    def __str__(self):
        return "The action is forbidden"

    def set_metadata(self, metadata: dict):
        pass

    @staticmethod
    def from_dict(as_dict):
        return AuthConstraintForbidden()


class AuthConstraint(AbstractAuthConstraint):
    def __init__(self, role, sig_count,
                 need_to_be_owner=False,
                 off_ledger_signature=None,
                 metadata={}):
        self._role_validation(role, off_ledger_signature)
        self.role = role
        self.sig_count = sig_count
        self.need_to_be_owner = need_to_be_owner
        self.off_ledger_signature = off_ledger_signature
        self.metadata = metadata
        self.constraint_id = ConstraintsEnum.ROLE_CONSTRAINT_ID

    @property
    def as_dict(self):
        constraint = {
            CONSTRAINT_ID: self.constraint_id,
            ROLE: self.role,
            SIG_COUNT: self.sig_count,
            NEED_TO_BE_OWNER: self.need_to_be_owner,
            METADATA: self.metadata
        }
        if self.off_ledger_signature is not None:
            constraint[OFF_LEDGER_SIGNATURE] = self.off_ledger_signature
        return constraint

    @staticmethod
    def _role_validation(role, off_ledger_signature):
        if role not in accepted_roles:
            raise ValueError("Role {} is not acceptable".format(role))
        if off_ledger_signature and role != "*":
            raise ValueError("'off_ledger_signature' can be set to True only if any role is accepted (role='*'). "
                             "Got {} role instead.".format(role))

    def __str__(self):
        role = get_named_role(self.role) if self.role != '*' else 'ALL'
        error_msg = ""

        if self.off_ledger_signature and self.sig_count > 1:
            error_msg = "{} signatures of any role (off-ledger included) are required".format(self.sig_count)
        elif self.off_ledger_signature and self.sig_count == 1:
            error_msg = "1 signature of any role (off-ledger included) is required"

        elif role != 'ALL' and self.need_to_be_owner and self.sig_count > 1:
            error_msg = "{} {} signatures are required and needs to be owner".format(self.sig_count, role)
        elif role != 'ALL' and not self.need_to_be_owner and self.sig_count > 1:
            error_msg = "{} {} signatures are required".format(self.sig_count, role)
        elif role != 'ALL' and not self.need_to_be_owner and self.sig_count == 1:
            error_msg = "1 {} signature is required".format(role)
        elif role != 'ALL' and self.need_to_be_owner and self.sig_count == 1:
            error_msg = "1 {} signature is required and needs to be owner".format(role)

        elif role == "ALL" and self.need_to_be_owner and self.sig_count == 1:
            error_msg = "1 signature of any role is required and needs to be owner"
        elif role == 'ALL' and not self.need_to_be_owner and self.sig_count == 1:
            error_msg = "1 signature of any role is required".format(role)
        elif role == 'ALL' and not self.need_to_be_owner and self.sig_count > 1:
            error_msg = "{} signatures of any role are required".format(self.sig_count)
        elif role == "ALL" and self.need_to_be_owner and self.sig_count > 1:
            error_msg = "{} signatures of any role are required and needs to be owner".format(self.sig_count)

        metadata_str = self._metadata_str()
        if metadata_str:
            return "{} {}".format(error_msg, metadata_str)
        return error_msg

    def _metadata_str(self):
        if not self.metadata:
            return ""
        res = " ".join([str(item) for values in self.metadata.items() for item in values])
        return "with additional metadata {}".format(res)

    @staticmethod
    def from_dict(as_dict):
        return AuthConstraint(role=as_dict[ROLE], sig_count=as_dict[SIG_COUNT],
                              need_to_be_owner=as_dict.get(NEED_TO_BE_OWNER, False),
                              off_ledger_signature=as_dict.get(OFF_LEDGER_SIGNATURE, None),
                              metadata=as_dict.get(METADATA, {}))

    def set_metadata(self, metadata: dict):
        self.metadata = metadata


class AuthConstraintAnd(AbstractAuthConstraint):
    def __init__(self, auth_constraints: List[AbstractAuthConstraint]):
        self.auth_constraints = auth_constraints
        self.constraint_id = ConstraintsEnum.AND_CONSTRAINT_ID

    @property
    def as_dict(self):
        return {
            CONSTRAINT_ID: self.constraint_id,
            AUTH_CONSTRAINTS: [c.as_dict for c in self.auth_constraints]
        }

    def __str__(self):
        return " AND ".join([str(ac) for ac in self.auth_constraints])

    @staticmethod
    def from_dict(as_dict):
        auth_constraints = []
        for input_constraint in as_dict[AUTH_CONSTRAINTS]:
            dict_constraint = dict(input_constraint)
            constraint_id = dict_constraint.pop(CONSTRAINT_ID)
            constraint_cls = constraint_to_class_map.get(constraint_id)
            auth_constraints.append(constraint_cls.from_dict(dict_constraint))
        as_dict[AUTH_CONSTRAINTS] = auth_constraints

        return AuthConstraintAnd(**as_dict)

    def set_metadata(self, metadata: dict):
        for constraint in self.auth_constraints:
            constraint.set_metadata(metadata)


class AuthConstraintOr(AbstractAuthConstraint):
    def __init__(self, auth_constraints: List[AbstractAuthConstraint]):
        self.auth_constraints = auth_constraints
        self.constraint_id = ConstraintsEnum.OR_CONSTRAINT_ID

    @property
    def as_dict(self):
        return {
            CONSTRAINT_ID: self.constraint_id,
            AUTH_CONSTRAINTS: [c.as_dict for c in self.auth_constraints]
        }

    def __str__(self):
        return " OR ".join([str(ac) for ac in self.auth_constraints])

    @staticmethod
    def from_dict(as_dict):
        auth_constraints = []
        for input_constraint in as_dict[AUTH_CONSTRAINTS]:
            dict_constraint = dict(input_constraint)
            constraint_id = dict_constraint.pop(CONSTRAINT_ID)
            if constraint_id is None:
                raise KeyError('There is no "constraint_id" field in deserialised dict: {}'.format(as_dict))
            constraint_cls = constraint_to_class_map.get(constraint_id)
            auth_constraints.append(constraint_cls.from_dict(dict_constraint))
        as_dict[AUTH_CONSTRAINTS] = auth_constraints

        return AuthConstraintOr(**as_dict)

    def set_metadata(self, metadata: dict):
        for constraint in self.auth_constraints:
            constraint.set_metadata(metadata)


class ConstraintCreator:
    @staticmethod
    def create_constraint(input_dict):
        as_dict = dict(input_dict)
        constraint_id = as_dict.pop(CONSTRAINT_ID)
        if constraint_id is None:
            raise KeyError('There is no "constraint_id" field in deserialised dict: {}'.format(as_dict))

        constraint_cls = constraint_to_class_map.get(constraint_id)
        return constraint_cls.from_dict(as_dict)


class AbstractConstraintSerializer(metaclass=ABCMeta):
    def __init__(self, serializer):
        self.serializer = serializer

    @abstractmethod
    def serialize(self, constraint: AbstractAuthConstraint) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self, serialized_str: bytes) -> AbstractAuthConstraint:
        raise NotImplementedError()


class ConstraintsSerializer(AbstractConstraintSerializer):
    def serialize(self, constraint: AbstractAuthConstraint) -> bytes:
        return self.serializer.serialize(constraint.as_dict if constraint else {})

    def deserialize(self, serialized_str: bytes) -> AbstractAuthConstraint:
        as_dict = self.serializer.deserialize(serialized_str)
        return ConstraintCreator.create_constraint(as_dict)


class AbstractAuthConstraintParser(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def is_accepted(constraint_results: List):
        raise NotImplementedError()


class AuthConstraintParserOr(AbstractAuthConstraintParser):
    @staticmethod
    def is_accepted(constraint_results: List):
        return any(constraint_results)


class AuthConstraintParserAnd(AbstractAuthConstraintParser):
    @staticmethod
    def is_accepted(constraint_results: List):
        return all(constraint_results)


constraint_to_class_map = {
    ConstraintsEnum.ROLE_CONSTRAINT_ID: AuthConstraint,
    ConstraintsEnum.AND_CONSTRAINT_ID: AuthConstraintAnd,
    ConstraintsEnum.OR_CONSTRAINT_ID: AuthConstraintOr,
    ConstraintsEnum.FORBIDDEN_CONSTRAINT_ID: AuthConstraintForbidden,
}
