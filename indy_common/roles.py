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
