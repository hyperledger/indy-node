from abc import ABCMeta, abstractmethod
from typing import List

from indy_common.authorize.helper import get_named_role

ROLE_CONSTRAINT_ID = 'ROLE'
AND_CONSTRAINT_ID = 'AND'
OR_CONSTRAINT_ID = 'OR'


class AbstractAuthConstraint(metaclass=ABCMeta):
    def __init__(self):
        self.constraint_id = ''

    def __str__(self):
        return str(self)


class AuthConstraint(AbstractAuthConstraint):
    def __init__(self, role, sig_count, need_to_be_owner=False, metadata={}):
        self.role = role
        self.sig_count = sig_count
        self.need_to_be_owner = need_to_be_owner
        self.metadata = metadata
        self.constraint_id = ROLE_CONSTRAINT_ID

    def __str__(self):
        role = get_named_role(self.role) if self.role != '*' else 'ALL'
        return "Required role: {}, Count of signatures: {}, Need to be owner: {}".format(role,
                                                                                         self.sig_count,
                                                                                         self.need_to_be_owner)


class AuthConstraintAnd(AbstractAuthConstraint):
    def __init__(self, auth_constraints):
        self.auth_constraints = auth_constraints
        self.constraint_id = AND_CONSTRAINT_ID

    def __str__(self):
        return " AND ".join([str(ac) for ac in self.auth_constraints])


class AuthConstraintOr(AbstractAuthConstraint):
    def __init__(self, auth_constraints):
        self.auth_constraints = auth_constraints
        self.constraint_id = OR_CONSTRAINT_ID

    def __str__(self):
        return " OR ".join([str(ac) for ac in self.auth_constraints])


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
