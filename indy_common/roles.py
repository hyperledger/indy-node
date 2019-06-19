from enum import Enum, unique

from plenum.common.roles import Roles


@unique
class Roles(Enum):
    #  These numeric constants CANNOT be changed once they have been used,
    #  because that would break backwards compatibility with the ledger
    #  Also the numeric constants CANNOT collide with the roles in plenum
    IDENTITY_OWNER = Roles.IDENTITY_OWNER.value
    TRUSTEE = Roles.TRUSTEE.value
    STEWARD = Roles.STEWARD.value
    ENDORSER = "101"
    NETWORK_MONITOR = "201"

    def __str__(self):
        return self.name

    @staticmethod
    def nameFromValue(value):
        # TODO: think about a term for a user with None role
        return Roles(value).name if value else 'None role'
