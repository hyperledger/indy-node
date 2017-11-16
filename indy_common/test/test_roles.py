#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from plenum.common.constants import STEWARD, TRUSTEE
from indy_common.constants import TGB, TRUST_ANCHOR
from indy_common.roles import Roles


def testRolesAreEncoded():
    assert STEWARD == "2"
    assert TRUSTEE == "0"
    assert TGB == "100"
    assert TRUST_ANCHOR == "101"


def testRolesEnumDecoded():
    assert Roles.STEWARD.name == "STEWARD"
    assert Roles.TRUSTEE.name == "TRUSTEE"
    assert Roles.TGB.name == "TGB"
    assert Roles.TRUST_ANCHOR.name == "TRUST_ANCHOR"


def testRolesEnumEncoded():
    assert Roles.STEWARD.value == "2"
    assert Roles.TRUSTEE.value == "0"
    assert Roles.TGB.value == "100"
    assert Roles.TRUST_ANCHOR.value == "101"


def testNameFromValue():
    assert Roles.nameFromValue("2") == "STEWARD"
    assert Roles.nameFromValue("0") == "TRUSTEE"
    assert Roles.nameFromValue("100") == "TGB"
    assert Roles.nameFromValue("101") == "TRUST_ANCHOR"
    assert Roles.nameFromValue(None) == "None role"
