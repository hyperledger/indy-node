from abc import ABCMeta, abstractmethod
from typing import List


ROLE_CONSTRAINT_ID = 'ROLE'
AND_CONSTRAINT_ID = 'AND'
OR_CONSTRAINT_ID = 'OR'


class AbstractAuthConstraint(metaclass=ABCMeta):
    def __init__(self):
        self.constraint_id = ''


class AuthConstraint(AbstractAuthConstraint):
    def __init__(self, role, sig_count, need_to_be_owner=False, metadata={}):
        self.role = role
        self.sig_count = sig_count
        self.need_to_be_owner = need_to_be_owner
        self.metadata = metadata
        self.constraint_id = ROLE_CONSTRAINT_ID


class AuthConstraintAnd(AbstractAuthConstraint):
    def __init__(self, auth_constraints):
        self.auth_constraints = auth_constraints
        self.constraint_id = AND_CONSTRAINT_ID


class AuthConstraintOr(AbstractAuthConstraint):
    def __init__(self, auth_constraints):
        self.auth_constraints = auth_constraints
        self.constraint_id = OR_CONSTRAINT_ID


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
