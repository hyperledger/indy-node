from plenum.common.constants import STEWARD, TRUSTEE
from indy_common.constants import TRUST_ANCHOR
from indy_common.roles import Roles


def testRolesAreEncoded():
    assert STEWARD == "2"
    assert TRUSTEE == "0"
    assert TRUST_ANCHOR == "101"


def testRolesEnumDecoded():
    assert Roles.STEWARD.name == "STEWARD"
    assert Roles.TRUSTEE.name == "TRUSTEE"
    assert Roles.TRUST_ANCHOR.name == "TRUST_ANCHOR"


def testRolesEnumEncoded():
    assert Roles.STEWARD.value == "2"
    assert Roles.TRUSTEE.value == "0"
    assert Roles.TRUST_ANCHOR.value == "101"


def testNameFromValue():
    assert Roles.nameFromValue("2") == "STEWARD"
    assert Roles.nameFromValue("0") == "TRUSTEE"
    assert Roles.nameFromValue("101") == "TRUST_ANCHOR"
    assert Roles.nameFromValue(None) == "None role"
