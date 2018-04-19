from plenum.common.constants import TRUSTEE

from indy_common.auth import Authoriser
from indy_common.constants import POOL_RESTART, ACTION, TGB


def test_pool_restart_start(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_RESTART,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal="aaa",
                                               newVal="start",
                                               isActorOwnerOfSubject=is_owner)[0]
