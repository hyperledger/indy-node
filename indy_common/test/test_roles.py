from plenum.common.constants import STEWARD, TRUSTEE
from indy_common.constants import ENDORSER
from indy_common.roles import Roles


def testRolesAreEncoded():
    assert STEWARD == "2"
    assert TRUSTEE == "0"
    assert ENDORSER == "101"


def testRolesEnumDecoded():
    assert Roles.STEWARD.name == "STEWARD"
    assert Roles.TRUSTEE.name == "TRUSTEE"
    assert Roles.ENDORSER.name == "ENDORSER"


def testRolesEnumEncoded():
    assert Roles.STEWARD.value == "2"
    assert Roles.TRUSTEE.value == "0"
    assert Roles.ENDORSER.value == "101"


def testNameFromValue():
    assert Roles.nameFromValue("2") == "STEWARD"
    assert Roles.nameFromValue("0") == "TRUSTEE"
    assert Roles.nameFromValue("101") == "ENDORSER"
    assert Roles.nameFromValue(None) == "None role"
