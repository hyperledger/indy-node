from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser
from indy_common.constants import NAME, TGB, TRUST_ANCHOR, SCHEMA


def test_schema_adding():
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_schemas(role)
        assert r and not msg


def test_schema_adding_without_permission():
    roles = {TGB, None}
    for role in roles:
        r, msg = _authorised_for_schemas(role)
        assert not r and msg


def _authorised_for_schemas(role):
    return Authoriser.authorised(typ=SCHEMA,
                                 actorRole=role)
