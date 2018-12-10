from typing import NamedTuple

from indy_common.auth_constraints import AuthConstraint, AuthConstraintOr
from indy_common.constants import ROLE
from plenum.common.constants import TRUSTEE, STEWARD, VERKEY

from abc import ABCMeta, abstractmethod

from indy_common.constants import OWNER, POOL_UPGRADE, TRUST_ANCHOR, NYM, \
    POOL_CONFIG, SCHEMA, CLAIM_DEF, \
    POOL_RESTART, VALIDATOR_INFO


RULE_DELIMETER = "--"
ADD_PREFIX = "ADD"
EDIT_PREFIX = "EDIT"

ActionDef = NamedTuple('ActionDef', [('prefix', str), ('txn_type', str), ('field', str), ('old_value', str), ('new_value', str)])


def compile_action_id(txn_type,
                      field,
                      old_value,
                      new_value,
                      prefix='') -> str:
    return RULE_DELIMETER.join([prefix,
                                txn_type,
                                field,
                                old_value,
                                new_value])


def split_action_id(action_id) -> ActionDef:
    return ActionDef(*action_id.split(RULE_DELIMETER))


"""

Action's classes

"""


class AbstractAuthAction(metaclass=ABCMeta):
    def __init__(self, txn_type):
        pass

    @abstractmethod
    def get_action_id(self):
        raise NotImplementedError()


class AuthActionAdd(AbstractAuthAction):
    def __init__(self, txn_type, field=None, value=None):
        self.txn_type = txn_type
        self.field = field
        self.value = value

    def get_action_id(self):
        return compile_action_id(txn_type=self.txn_type,
                                 field=self.field,
                                 old_value='*',
                                 new_value=self.value,
                                 prefix=ADD_PREFIX)


class AuthActionEdit(AbstractAuthAction):
    def __init__(self, txn_type, field=None, old_value=None, new_value=None):
        self.txn_type = txn_type
        self.field = field
        self.old_value = old_value
        self.new_value = new_value

    def get_action_id(self):
        return compile_action_id(txn_type=self.txn_type,
                                 field=self.field,
                                 old_value=self.old_value,
                                 new_value=self.new_value,
                                 prefix=EDIT_PREFIX)


addNewTrustee = AuthActionAdd(txn_type=NYM,
                              field=ROLE,
                              value=TRUSTEE)

addNewSteward = AuthActionAdd(txn_type=NYM,
                              field=ROLE,
                              value=STEWARD)

addNewTrustAnchor = AuthActionAdd(txn_type=NYM,
                                  field=ROLE,
                                  value=TRUST_ANCHOR)


addNewIdentityOwner = AuthActionAdd(txn_type=NYM,
                                    field='*',
                                    value='*')


blacklistingTrustee = AuthActionEdit(txn_type=NYM,
                                     field=ROLE,
                                     old_value=TRUSTEE,
                                     new_value='')

blacklistingSteward = AuthActionEdit(txn_type=NYM,
                                     field=ROLE,
                                     old_value=STEWARD,
                                     new_value='')

blacklistingTrustAnchor = AuthActionEdit(txn_type=NYM,
                                         field=ROLE,
                                         old_value=TRUST_ANCHOR,
                                         new_value='')

keyRotation = AuthActionEdit(txn_type=NYM,
                             field=VERKEY,
                             old_value='*',
                             new_value='*')


auth_map = {addNewTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
            addNewSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
            addNewTrustAnchor.get_action_id(): AuthConstraint(TRUST_ANCHOR, 1),
            addNewIdentityOwner.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                                   AuthConstraint(STEWARD, 1),
                                                                   AuthConstraint(TRUST_ANCHOR, 1)]),
            blacklistingTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
            blacklistingSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
            blacklistingTrustAnchor.get_action_id(): AuthConstraint(TRUSTEE, 1),
            keyRotation.get_action_id(): AuthConstraint(role='*',
                                                        sig_count=1,
                                                        need_to_be_owner=True)}
