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

from plenum.common.constants import NODE, TRUSTEE, BLS_KEY, STEWARD

from indy_common.auth import Authoriser


def test_node_not_allowed_role_error():
    expected_msg = "TRUSTEE not in allowed roles ['STEWARD']"
    assert expected_msg == Authoriser.authorised(typ=NODE,
                                                 field=BLS_KEY,
                                                 actorRole=TRUSTEE,
                                                 oldVal=None,
                                                 newVal="some_value",
                                                 isActorOwnerOfSubject=False)[1]


def test_node_only_owner_error():
    expected_msg = "Only owner is allowed"
    assert expected_msg == Authoriser.authorised(typ=NODE,
                                                 field=BLS_KEY,
                                                 actorRole=STEWARD,
                                                 oldVal=None,
                                                 newVal="some_value",
                                                 isActorOwnerOfSubject=False)[1]
