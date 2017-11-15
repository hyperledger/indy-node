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
