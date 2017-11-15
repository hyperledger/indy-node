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
