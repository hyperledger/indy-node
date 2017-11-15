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

from plenum.common.constants import TRUSTEE, STEWARD, VERKEY

from indy_common.auth import Authoriser
from indy_common.constants import ROLE, NYM, TGB, TRUST_ANCHOR


def test_make_trustee(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal=TRUSTEE,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_make_tgb(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal=TGB,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_make_steward(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal=STEWARD,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_make_trust_anchor(role, is_owner):
    authorized = role in (TRUSTEE, STEWARD)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal=TRUST_ANCHOR,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_remove_trustee(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=TRUSTEE,
                                               newVal=None,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_remove_tgb(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=TGB,
                                               newVal=None,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_remove_steward(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=STEWARD,
                                               newVal=None,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_remove_trust_anchor(role, is_owner):
    authorized = (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=ROLE,
                                               actorRole=role,
                                               oldVal=TRUST_ANCHOR,
                                               newVal=None,
                                               isActorOwnerOfSubject=is_owner)[0]


def test_change_verkey(role, is_owner, old_values):
    authorized = is_owner
    assert authorized == Authoriser.authorised(typ=NYM,
                                               field=VERKEY,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]
