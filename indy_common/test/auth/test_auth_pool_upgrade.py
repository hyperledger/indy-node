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

from plenum.common.constants import TRUSTEE

from indy_common.auth import Authoriser
from indy_common.constants import POOL_UPGRADE, ACTION, TGB


def test_pool_upgrade_start(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal="start",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_cancel(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal="start",
                                               newVal="cancel",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_old_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     field=ACTION,
                                     actorRole=role,
                                     oldVal="aaa",
                                     newVal="cancel",
                                     isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_new_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     field=ACTION,
                                     actorRole=role,
                                     oldVal="start",
                                     newVal="aaa",
                                     isActorOwnerOfSubject=is_owner)[0]
