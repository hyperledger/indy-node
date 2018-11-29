import re
from typing import Dict, List, NamedTuple

from indy_common.constants import NYM, LOCAL_AUTH_POLICY, CONFIG_LEDGER_AUTH_POLICY
from plenum.common.constants import TRUSTEE, STEWARD

from abc import ABCMeta, abstractmethod

from indy_common.constants import OWNER, POOL_UPGRADE, TRUST_ANCHOR, NYM, \
    POOL_CONFIG, SCHEMA, CLAIM_DEF, \
    POOL_RESTART, VALIDATOR_INFO


RULE_DELIMETER = "--"

def compile_rule_id(txn_type,
                    field,
                    old_value,
                    new_value) -> str:
    return RULE_DELIMETER.join([txn_type,
                                field,
                                old_value,
                                new_value])

"""

Definition for one auth constraint (for example, ('TRUSTEE', 3))

"""

RoleDef = NamedTuple('Roledef', [('role', str), ('sig_count', int)])

"""

Combined auth constraints (for example, [('TRUSTEE', 3), ('STEWARD', 7)])

"""

class AuthConstraint(List[RoleDef]):
    """
    'AND' strategy implemented. If there is several RoleDefs, then all of this must be presented in incomming constraints
    """
    def is_accepted(self, other_constraint):
        compares = []
        for r in other_constraint:
            for s in self:
                if r.role == s.role and s.sig_count <= r.sig_count:
                    compares.append(True)
        return len(self) == len(compares) and all(compares)

"""

Rule's classes

"""


class AbstractRule(metaclass=ABCMeta):
    def __init__(self,
                 description: str,
                 txn_type: str,
                 default_auth_constraint: AuthConstraint,
                 rule_id='',
                 field='*',
                 old_value='*',
                 new_value='*'):
        self.description = description
        self.txn_type = txn_type
        self.rule_id = rule_id
        self.default_auth_constraint = default_auth_constraint
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.allow_field = False
        self.allow_old_value = False
        self.allow_new_value = False
        self.allow_for_all = False
        self._create_rule_id()
        self._preprocessing()

    def _create_rule_id(self) -> str:
        if not self.rule_id:
            self.rule_id = compile_rule_id(self.txn_type,
                                           self.field,
                                           self.old_value,
                                           self.new_value)

    @abstractmethod
    def _preprocessing(self):
        raise NotImplementedError()


class RuleAdd(AbstractRule):
    def _preprocessing(self):
        self.allow_old_value = True
        if self.field == '*':
            self.allow_field = True
        if self.new_value == '*':
            self.allow_new_value = True
        if self.default_auth_constraint == []:
            self.allow_for_all = True

class RuleRemove(AbstractRule):
    def _preprocessing(self):
        self.allow_old_value = True
        self.allow_new_value = True
        if self.field == '*':
            self.allow_field = True
        if self.default_auth_constraint == []:
            self.allow_for_all = True

class RuleEdit(AbstractRule):
    def _preprocessing(self):
        if self.field == '*':
            self.allow_field = True
        if self.old_value == '*':
            self.allow_old_value = True
        if self.new_value == '*':
            self.allow_new_value = True
        if self.default_auth_constraint == []:
            self.allow_for_all = True

"""

Policy's clases

"""

class AbstractAuthPolicy(metaclass=ABCMeta):
    def __init__(self, auth_map):
        self.auth_map = auth_map

    @abstractmethod
    def get_auth_constraint(self, rule_id) -> AuthConstraint:
        raise NotImplementedError()


class LocalAuthPolicy(AbstractAuthPolicy):

    def get_auth_constraint(self, rule_id) -> AuthConstraint:
        return self.auth_map.get(rule_id, None)


class ConfigLedgerAuthPolicy(AbstractAuthPolicy):

    def get_auth_constraint(self, rule_id) -> AuthConstraint:
        """Get constraints from config ledger"""
        pass


"""

Main class for authorization

"""


class Authorizer():
    def __init__(self, auth_map, config):
        self.config = config
        if self.config.authPolicy == LOCAL_AUTH_POLICY:
            self.policy = LocalAuthPolicy(auth_map)
        elif self.config.authPolicy == CONFIG_LEDGER_AUTH_POLICY:
            self.policy = ConfigLedgerAuthPolicy(auth_map)

    def find_rule(self,
                  txn_type,
                  field='*',
                  old_value='*',
                  new_value='*') -> AbstractRule:
        rule_id = compile_rule_id(txn_type,
                                  field,
                                  old_value,
                                  new_value)
        for key in self.policy.auth_map.keys():
            if re.match(key, rule_id):
                return self.policy.auth_map.get(key)

    def authorize(self,
                  txn_type,
                  field='*',
                  old_value='*',
                  new_value='*',
                  auth_constraint=AuthConstraint()) -> bool:
        rule = self.find_rule(txn_type=txn_type,
                              field=field,
                              old_value=old_value,
                              new_value=new_value)
        rule_auth_constraint = self.policy.get_auth_constraint(rule.rule_id)
        return self._do_authorize(field=field,
                                  old_value=old_value,
                                  new_value=new_value,
                                  rule=rule,
                                  rule_auth_constraint=rule_auth_constraint,
                                  auth_constraint=auth_constraint)

    def _do_authorize(self,
                      field: str,
                      old_value: str,
                      new_value: str,
                      rule: AbstractRule,
                      rule_auth_constraint: AuthConstraint,
                      auth_constraint: AuthConstraint) -> bool:
        if not rule.allow_field and rule.field != field:
            return False
        if not rule.allow_old_value and rule.old_value != old_value:
            return False
        if not rule.allow_new_value and rule.new_value != new_value:
            return False
        if not rule.allow_for_all and rule_auth_constraint.is_accepted(auth_constraint):
            return False
        return True


addNewTrustee = RuleAdd(txn_type=NYM,
                        field='role',
                        new_value=TRUSTEE,
                        default_auth_constraint=[{TRUSTEE: 1}],
                        description="Add new trustee")

addNewSteward = RuleAdd(txn_type=NYM,
                        field='role',
                        new_value=STEWARD,
                        default_auth_constraint=[{TRUSTEE: 1}],
                        description="Add new steward")

