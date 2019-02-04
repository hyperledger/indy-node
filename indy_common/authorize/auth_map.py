from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_constraints import AuthConstraint, AuthConstraintOr
from indy_common.constants import TRUST_ANCHOR, POOL_CONFIG, VALIDATOR_INFO, POOL_UPGRADE, POOL_RESTART, NODE, \
    CLAIM_DEF, SCHEMA, NYM, ROLE, NETWORK_MONITOR
from plenum.common.constants import TRUSTEE, STEWARD, VERKEY


addNewTrustee = AuthActionAdd(txn_type=NYM,
                              field=ROLE,
                              value=TRUSTEE)

addNewSteward = AuthActionAdd(txn_type=NYM,
                              field=ROLE,
                              value=STEWARD)

addNewTrustAnchor = AuthActionAdd(txn_type=NYM,
                                  field=ROLE,
                                  value=TRUST_ANCHOR)

addNewNetworkMonitor = AuthActionAdd(txn_type=NYM,
                                     field=ROLE,
                                     value=NETWORK_MONITOR)


addNewIdentityOwner = AuthActionAdd(txn_type=NYM,
                                    field=ROLE,
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

blacklistingNetworkMonitor = AuthActionEdit(txn_type=NYM,
                                            field=ROLE,
                                            old_value=NETWORK_MONITOR,
                                            new_value='')

sameRoleTrustee = AuthActionEdit(txn_type=NYM,
                                 field=ROLE,
                                 old_value=TRUSTEE,
                                 new_value=TRUSTEE)

sameRoleSteward = AuthActionEdit(txn_type=NYM,
                                 field=ROLE,
                                 old_value=STEWARD,
                                 new_value=STEWARD)

sameRoleTrustAnchor = AuthActionEdit(txn_type=NYM,
                                     field=ROLE,
                                     old_value=TRUST_ANCHOR,
                                     new_value=TRUST_ANCHOR)

sameRoleNetworkMonitor = AuthActionEdit(txn_type=NYM,
                                        field=ROLE,
                                        old_value=NETWORK_MONITOR,
                                        new_value=NETWORK_MONITOR)

sameRoleNone = AuthActionEdit(txn_type=NYM,
                              field=ROLE,
                              old_value='',
                              new_value='')

keyRotation = AuthActionEdit(txn_type=NYM,
                             field=VERKEY,
                             old_value='*',
                             new_value='*')

addSchema = AuthActionAdd(txn_type=SCHEMA,
                          field='*',
                          value='*')

editSchema = AuthActionEdit(txn_type=SCHEMA,
                            field='*',
                            old_value='*',
                            new_value='*')

addClaimDef = AuthActionAdd(txn_type=CLAIM_DEF,
                            field='*',
                            value='*')

editClaimDef = AuthActionEdit(txn_type=CLAIM_DEF,
                              field='*',
                              old_value='*',
                              new_value='*')


addingNewNode = AuthActionAdd(txn_type=NODE,
                              field='services',
                              value='[\'VALIDATOR\']')

demoteNode = AuthActionEdit(txn_type=NODE,
                            field='services',
                            old_value='[\'VALIDATOR\']',
                            new_value='[]')

promoteNode = AuthActionEdit(txn_type=NODE,
                             field='services',
                             old_value='[]',
                             new_value='[\'VALIDATOR\']')


changeNodeIp = AuthActionEdit(txn_type=NODE,
                              field='node_ip',
                              old_value='*',
                              new_value='*')

changeNodePort = AuthActionEdit(txn_type=NODE,
                                field='node_port',
                                old_value='*',
                                new_value='*')

changeClientIp = AuthActionEdit(txn_type=NODE,
                                field='client_ip',
                                old_value='*',
                                new_value='*')

changeClientPort = AuthActionEdit(txn_type=NODE,
                                  field='client_port',
                                  old_value='*',
                                  new_value='*')

changeBlsKey = AuthActionEdit(txn_type=NODE,
                              field='blskey',
                              old_value='*',
                              new_value='*')

startUpgrade = AuthActionAdd(txn_type=POOL_UPGRADE,
                             field='action',
                             value='start')

cancelUpgrade = AuthActionEdit(txn_type=POOL_UPGRADE,
                               field='action',
                               old_value='start',
                               new_value='cancel')

poolRestart = AuthActionAdd(txn_type=POOL_RESTART,
                            field='action',
                            value='*')

poolConfig = AuthActionEdit(txn_type=POOL_CONFIG,
                            field='action',
                            old_value='*',
                            new_value='*')

validatorInfo = AuthActionAdd(txn_type=VALIDATOR_INFO,
                              field='*',
                              value='*')

anyoneCanAddNYM = AuthActionAdd(txn_type=NYM,
                                field=ROLE,
                                value='*')

anyoneCanAddSchema = AuthActionAdd(txn_type=SCHEMA,
                                   field='*',
                                   value='*')

anyoneCanAddClaimDef = AuthActionAdd(txn_type=CLAIM_DEF,
                                     field='*',
                                     value='*')

anyoneCanEditNYM = AuthActionEdit(txn_type=NYM,
                                  field=ROLE,
                                  old_value='*',
                                  new_value='*')

anyoneCanEditSchema = AuthActionEdit(txn_type=SCHEMA,
                                     field='*',
                                     old_value='*',
                                     new_value='*')

anyoneCanEditClaimDef = AuthActionEdit(txn_type=CLAIM_DEF,
                                       field='*',
                                       old_value='*',
                                       new_value='*')

authMap = {addNewTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
           addNewSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
           addNewTrustAnchor.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                                AuthConstraint(STEWARD, 1)]),
           addNewNetworkMonitor.get_action_id(): AuthConstraintOr([AuthConstraint(STEWARD, 1),
                                                                   AuthConstraint(TRUSTEE, 1)]),
           addNewIdentityOwner.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                                  AuthConstraint(STEWARD, 1),
                                                                  AuthConstraint(TRUST_ANCHOR, 1)]),
           blacklistingTrustee.get_action_id(): AuthConstraint(TRUSTEE, 1),
           blacklistingSteward.get_action_id(): AuthConstraint(TRUSTEE, 1),
           blacklistingTrustAnchor.get_action_id(): AuthConstraint(TRUSTEE, 1),
           blacklistingNetworkMonitor.get_action_id(): AuthConstraintOr([AuthConstraint(STEWARD, 1),
                                                                         AuthConstraint(TRUSTEE, 1)]),
           sameRoleTrustee.get_action_id(): AuthConstraint(role='*',
                                                           sig_count=1,
                                                           need_to_be_owner=True),
           sameRoleSteward.get_action_id(): AuthConstraint(role='*',
                                                           sig_count=1,
                                                           need_to_be_owner=True),
           sameRoleTrustAnchor.get_action_id(): AuthConstraint(role='*',
                                                               sig_count=1,
                                                               need_to_be_owner=True),
           sameRoleNone.get_action_id(): AuthConstraint(role='*',
                                                        sig_count=1,
                                                        need_to_be_owner=True),
           sameRoleNetworkMonitor.get_action_id(): AuthConstraint(role="*",
                                                                  sig_count=1,
                                                                  need_to_be_owner=True),
           keyRotation.get_action_id(): AuthConstraint(role='*',
                                                       sig_count=1,
                                                       need_to_be_owner=True),
           addSchema.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                        AuthConstraint(STEWARD, 1),
                                                        AuthConstraint(TRUST_ANCHOR, 1)]),
           editSchema.get_action_id(): AuthConstraint(None, 1),
           addClaimDef.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                          AuthConstraint(STEWARD, 1),
                                                          AuthConstraint(TRUST_ANCHOR, 1)]),
           editClaimDef.get_action_id(): AuthConstraint('*', 1, need_to_be_owner=True),
           addingNewNode.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           demoteNode.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                         AuthConstraint(STEWARD, 1, need_to_be_owner=True)]),
           promoteNode.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                          AuthConstraint(STEWARD, 1, need_to_be_owner=True)]),
           changeNodeIp.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           changeNodePort.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           changeClientIp.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           changeClientPort.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           changeBlsKey.get_action_id(): AuthConstraint(STEWARD, 1, need_to_be_owner=True),
           startUpgrade.get_action_id(): AuthConstraint(TRUSTEE, 1),
           cancelUpgrade.get_action_id(): AuthConstraint(TRUSTEE, 1),
           poolRestart.get_action_id(): AuthConstraint(TRUSTEE, 1),
           poolConfig.get_action_id(): AuthConstraint(TRUSTEE, 1),
           validatorInfo.get_action_id(): AuthConstraintOr([AuthConstraint(TRUSTEE, 1),
                                                            AuthConstraint(STEWARD, 1),
                                                            AuthConstraint(NETWORK_MONITOR, 1)])}

anyoneCanWriteMap = {anyoneCanAddNYM.get_action_id(): AuthConstraint(role='*',
                                                                     sig_count=1),
                     anyoneCanAddSchema.get_action_id(): AuthConstraint(role='*',
                                                                        sig_count=1),
                     anyoneCanAddClaimDef.get_action_id(): AuthConstraint(role='*',
                                                                          sig_count=1,
                                                                          need_to_be_owner=True),
                     anyoneCanEditNYM.get_action_id(): AuthConstraint(role='*',
                                                                      sig_count=1),
                     anyoneCanEditSchema.get_action_id(): AuthConstraint(role='*',
                                                                         sig_count=1),
                     anyoneCanEditClaimDef.get_action_id(): AuthConstraint(role='*',
                                                                           sig_count=1,
                                                                           need_to_be_owner=True)}
