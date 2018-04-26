from plenum.common.constants import TRUSTEE

from indy_common.auth import Authoriser
from indy_common.constants import POOL_UPGRADE, ACTION, TGB


def test_pool_upgrade_start(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               actorRole=role,
                                               field=ACTION,
                                               oldVal=None,
                                               newVal="start",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_cancel(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               actorRole=role,
                                               field=ACTION,
                                               oldVal="start",
                                               newVal="cancel",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_old_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     actorRole=role,
                                     field=ACTION,
                                     oldVal="aaa",
                                     newVal="cancel",
                                     isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_new_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     actorRole=role,
                                     field=ACTION,
                                     oldVal="start",
                                     newVal="aaa",
                                     isActorOwnerOfSubject=is_owner)[0]
