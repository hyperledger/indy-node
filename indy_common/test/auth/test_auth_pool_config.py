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

from plenum.common.constants import TRUSTEE, BLS_KEY

from indy_common.auth import Authoriser
from indy_common.constants import TGB, POOL_CONFIG, ACTION


def test_pool_config_change(role, is_owner, old_values):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_CONFIG,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]
