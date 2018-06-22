from plenum.common.constants import TRUSTEE, STEWARD, NODE
from stp_core.common.log import getlogger

from indy_common.constants import OWNER, POOL_UPGRADE, TGB, TRUST_ANCHOR, NYM, \
    POOL_CONFIG, SCHEMA, CLAIM_DEF, \
    POOL_RESTART, VALIDATOR_INFO
from indy_common.roles import Roles

logger = getlogger()


# TODO: make this class the only point of authorization and checking permissions!
# There are some duplicates of this logic in *_req_handler classes

class Authoriser:
    ValidRoles = (TRUSTEE, TGB, STEWARD, TRUST_ANCHOR, None)

    AuthMap = {
        '{}_role__{}'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, TGB):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, TRUST_ANCHOR):
            {TRUSTEE: [], STEWARD: []},
        '{}_role__'.format(NYM):
            {TRUSTEE: [], TGB: [], STEWARD: [], TRUST_ANCHOR: []},
        '{}_role_{}_'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, TGB):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, TRUST_ANCHOR):
            {TRUSTEE: []},
        '{}_<any>_<any>_<any>'.format(SCHEMA):
            {TRUSTEE: [], STEWARD: [], TRUST_ANCHOR: []},
        '{}_<any>_<any>_<any>'.format(CLAIM_DEF):
            {TRUSTEE: [OWNER, ], STEWARD: [OWNER, ], TRUST_ANCHOR: [OWNER, ]},
        '{}_verkey_<any>_<any>'.format(NYM):
            {r: [OWNER] for r in ValidRoles},
        '{}_services__[VALIDATOR]'.format(NODE):
            {STEWARD: [OWNER, ]},
        # INDY-410 - steward allowed to demote/promote its validator
        '{}_services_[VALIDATOR]_[]'.format(NODE):
            {TRUSTEE: [], STEWARD: [OWNER, ]},
        '{}_services_[]_[VALIDATOR]'.format(NODE):
            {TRUSTEE: [], STEWARD: [OWNER, ]},
        '{}_node_ip_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_node_port_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_client_ip_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_client_port_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_blskey_<any>_<any>'.format(NODE):
            {STEWARD: [OWNER, ]},
        '{}_action__start'.format(POOL_UPGRADE):
            {TRUSTEE: [], TGB: []},
        '{}_action_start_cancel'.format(POOL_UPGRADE):
            {TRUSTEE: [], TGB: []},
        '{}_action_<any>_<any>'.format(POOL_RESTART):
            {TRUSTEE: []},
        '{}_action_<any>_<any>'.format(POOL_CONFIG):
            {TRUSTEE: [], TGB: []},
        '{}_<any>_<any>_<any>'.format(VALIDATOR_INFO):
            {TRUSTEE: [], STEWARD: []},
    }

    @staticmethod
    def isValidRole(role) -> bool:
        return role in Authoriser.ValidRoles

    @staticmethod
    def getRoleFromName(roleName) -> bool:
        if not roleName:
            return
        return Roles[roleName].value

    @staticmethod
    def isValidRoleName(roleName) -> bool:
        if not roleName:
            return True

        try:
            Authoriser.getRoleFromName(roleName)
        except KeyError:
            return False

        return True

    @staticmethod
    def authorised(typ, actorRole, field=None, oldVal=None, newVal=None,
                   isActorOwnerOfSubject=None) -> (bool, str):
        field = field if field is not None else ""
        oldVal = '' if oldVal is None else \
            str(oldVal).replace('"', '').replace("'", '')
        newVal = '' if newVal is None else \
            str(newVal).replace('"', '').replace("'", '')
        key = '_'.join([typ, field, oldVal, newVal])
        if key not in Authoriser.AuthMap:
            any_value = '_'.join([typ, field, '<any>', '<any>'])
            if any_value not in Authoriser.AuthMap:
                any_field = '_'.join([typ, "<any>", '<any>', '<any>'])
                if any_field not in Authoriser.AuthMap:
                    msg = "key '{}' not found in authorized map".format(key)
                    logger.debug(msg)
                    return False, msg
                else:
                    key = any_field
            else:
                key = any_value
        roles = Authoriser.AuthMap[key]
        if actorRole not in roles:
            roles_as_str = [Roles.nameFromValue(role) for role in roles.keys()]
            return False, '{} not in allowed roles {}'.\
                format(Roles.nameFromValue(actorRole), roles_as_str)
        roleDetails = roles[actorRole]
        if len(roleDetails) == 0:
            return True, ''
        else:
            r = OWNER in roleDetails and isActorOwnerOfSubject
            msg = '' if r else 'Only owner is allowed'
            return r, msg
