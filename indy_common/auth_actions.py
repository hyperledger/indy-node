from typing import NamedTuple

from indy_common.auth_constraints import AuthConstraint, AuthConstraintOr
from indy_common.constants import ROLE, NODE
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
                                    field='role',
                                    value='')


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


AddSchema = AuthActionAdd(txn_type=SCHEMA,
                          field='*',
                          value='*')

AddClaimDef = AuthActionAdd(txn_type=CLAIM_DEF,
                            field='*',
                            value='*')

EditClaimDef = AuthActionEdit(txn_type=CLAIM_DEF,
                              field='*',
                              old_value='*',
                              new_value='*')


AddingNewNode = AuthActionAdd(txn_type=NODE,
                              field='services',
                              value='[VALIDATOR]')

DemoteNode = AuthActionEdit(txn_type=NODE,
                            field='services',
                            old_value='[VALIDATOR]',
                            new_value='[]')

PromoteNode = AuthActionEdit(txn_type=NODE,
                             field='services',
                             old_value='[]',
                             new_value='[VALIDATOR]')


ChangeNodeIp = AuthActionEdit(txn_type=NODE,
                              field='node_ip',
                              old_value='*',
                              new_value='*')

ChangeNodePort = AuthActionEdit(txn_type=NODE,
                                field='node_port',
                                old_value='*',
                                new_value='*')

ChangeClientIp = AuthActionEdit(txn_type=NODE,
                                field='client_ip',
                                old_value='*',
                                new_value='*')

ChangeClientPort = AuthActionEdit(txn_type=NODE,
                                  field='client_port',
                                  old_value='*',
                                  new_value='*')

ChangeBlsKey = AuthActionEdit(txn_type=NODE,
                              field='blskey',
                              old_value='*',
                              new_value='*')

StartUpgrade = AuthActionAdd(txn_type=POOL_UPGRADE,
                             field='action',
                             value='start')

CancelUpgrade = AuthActionEdit(txn_type=POOL_UPGRADE,
                               field='action',
                               old_value='start',
                               new_value='cancel')

PoolRestart = AuthActionAdd(txn_type=POOL_RESTART,
                            field='action',
                            value='*')

PoolConfig = AuthActionAdd(txn_type=POOL_CONFIG,
                           field='action',
                           value='*')

ValidatorInfo = AuthActionAdd(txn_type=VALIDATOR_INFO,
                              field='*',
                              value='*')

auth_map = {addNewTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
            addNewSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
            addNewTrustAnchor.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                                 AuthConstraint(STEWARD, 1)]),
            addNewIdentityOwner.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                                   AuthConstraint(STEWARD, 1),
                                                                   AuthConstraint(TRUST_ANCHOR, 1)]),
            blacklistingTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
            blacklistingSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
            blacklistingTrustAnchor.get_action_id(): AuthConstraint(TRUSTEE, 1),
            keyRotation.get_action_id(): AuthConstraint(role='*',
                                                        sig_count=1,
                                                        need_to_be_owner=True),
            AddSchema.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                         AuthConstraint(STEWARD, 1),
                                                         AuthConstraint(TRUST_ANCHOR, 1)]),
            AddClaimDef.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                           AuthConstraint(STEWARD, 1),
                                                           AuthConstraint(TRUST_ANCHOR, 1)]),
            EditClaimDef.get_action_id(): AuthConstraint('*', 1, need_to_be_owner=True),
            AddingNewNode.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            DemoteNode.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                          AuthConstraint(STEWARD, 1, need_to_be_owner=True)]),
            PromoteNode.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                          AuthConstraint(STEWARD, 1, need_to_be_owner=True)]),
            ChangeNodeIp.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            ChangeNodePort.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            ChangeClientIp.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            ChangeClientPort.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            ChangeBlsKey.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
            StartUpgrade.get_action_id(): AuthConstraint(TRUSTEE, 1),
            CancelUpgrade.get_action_id(): AuthConstraint(TRUSTEE, 1),
            PoolRestart.get_action_id(): AuthConstraint(TRUSTEE, 1),
            PoolConfig.get_action_id(): AuthConstraint(TRUSTEE, 1),
            ValidatorInfo.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                             AuthConstraint(STEWARD, 1)])}
