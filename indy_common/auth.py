from indy_common.config_util import getConfig
from plenum.common.constants import TRUSTEE, STEWARD, NODE, LEDGERS_FREEZE
from stp_core.common.log import getlogger

from indy_common.constants import OWNER, POOL_UPGRADE, ENDORSER, NYM, \
    POOL_CONFIG, SCHEMA, CLAIM_DEF, \
    POOL_RESTART, VALIDATOR_INFO, NETWORK_MONITOR
from indy_common.roles import Roles

logger = getlogger()


# TODO: make this class the only point of authorization and checking permissions!
# There are some duplicates of this logic in *_req_handler classes

def generate_auth_map(valid_roles):
    auth_map = {
        '{}_role__{}'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role__{}'.format(NYM, ENDORSER):
            {TRUSTEE: [], STEWARD: []},
        '{}_role__'.format(NYM):
            {TRUSTEE: [], STEWARD: [], ENDORSER: []},
        '{}_role_{}_'.format(NYM, TRUSTEE):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, STEWARD):
            {TRUSTEE: []},
        '{}_role_{}_'.format(NYM, ENDORSER):
            {TRUSTEE: []},
        '{}_<any>_<any>_<any>'.format(SCHEMA):
            {TRUSTEE: [], STEWARD: [], ENDORSER: []},
        '{}_<any>_<any>_<any>'.format(CLAIM_DEF):
            {TRUSTEE: [OWNER, ], STEWARD: [OWNER, ], ENDORSER: [OWNER, ]},
        '{}_verkey_<any>_<any>'.format(NYM):
            {r: [OWNER] for r in valid_roles},
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
            {TRUSTEE: []},
        '{}_action_start_cancel'.format(POOL_UPGRADE):
            {TRUSTEE: []},
        '{}_action_<any>_<any>'.format(POOL_RESTART):
            {TRUSTEE: []},
        '{}_action_<any>_<any>'.format(POOL_CONFIG):
            {TRUSTEE: []},
        '{}_<any>_<any>_<any>'.format(VALIDATOR_INFO):
            {TRUSTEE: [], STEWARD: []},
        '{}_<any>_<any>_<any>'.format(LEDGERS_FREEZE):
            {TRUSTEE: []},
    }
    return auth_map


class Authoriser:
    ValidRoles = (TRUSTEE, STEWARD, ENDORSER, NETWORK_MONITOR, None)

    auth_map = None

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
        if not Authoriser.auth_map:
            Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles)
        field = field if field is not None else ""
        oldVal = '' if oldVal is None else \
            str(oldVal).replace('"', '').replace("'", '')
        newVal = '' if newVal is None else \
            str(newVal).replace('"', '').replace("'", '')
        key = '_'.join([typ, field, oldVal, newVal])
        if key not in Authoriser.auth_map:
            any_value = '_'.join([typ, field, '<any>', '<any>'])
            if any_value not in Authoriser.auth_map:
                any_field = '_'.join([typ, "<any>", '<any>', '<any>'])
                if any_field not in Authoriser.auth_map:
                    msg = "key '{}' not found in authorized map".format(key)
                    logger.debug(msg)
                    return False, msg
                else:
                    key = any_field
            else:
                key = any_value
        roles = Authoriser.auth_map[key]
        if actorRole not in roles:
            roles_as_str = [Roles.nameFromValue(role) for role in roles.keys()]
            return False, '{} not in allowed roles {}'. \
                format(Roles.nameFromValue(actorRole), roles_as_str)
        roleDetails = roles[actorRole]
        if len(roleDetails) == 0:
            return True, ''
        else:
            r = OWNER in roleDetails and isActorOwnerOfSubject
            msg = '' if r else 'Only owner is allowed'
            return r, msg
