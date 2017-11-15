from enum import Enum, unique

from plenum.common.roles import Roles


@unique
class Roles(Enum):
    #  These numeric constants CANNOT be changed once they have been used,
    #  because that would break backwards compatibility with the ledger
    #  Also the numeric constants CANNOT collide with the roles in plenum
    TRUSTEE = Roles.TRUSTEE.value
    STEWARD = Roles.STEWARD.value
    TGB = "100"
    TRUST_ANCHOR = "101"

    def __str__(self):
        return self.name

    @staticmethod
    def nameFromValue(value):
        # TODO: think about a term for a user with None role
        return Roles(value).name if value else 'None role'
