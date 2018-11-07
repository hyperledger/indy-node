from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser
from indy_common.constants import VALIDATOR_INFO


def test_permission_for_validator_info(role):
    authorized = role in (TRUSTEE, STEWARD)
    assert authorized == Authoriser.authorised(typ=VALIDATOR_INFO,
                                               actorRole=role)[0]
