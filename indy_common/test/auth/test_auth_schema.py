from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser, generate_auth_map
from indy_common.constants import NAME, TRUST_ANCHOR, SCHEMA


def test_schema_adding(initialized_auth_map):
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_schemas(role)
        assert r and not msg


def test_schema_adding_without_permission(initialized_auth_map):
    r, msg = _authorised_for_schemas(None)
    assert not r and msg


def test_client_can_send_claim_def():
    Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles, True)

    r, msg = _authorised_for_schemas(None)
    assert r and not msg


def test_client_cant_send_claim_def():
    Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles, False)

    r, msg = _authorised_for_schemas(None)
    assert not r and "None role not in allowed roles" in msg


def _authorised_for_schemas(role):
    return Authoriser.authorised(typ=SCHEMA,
                                 actorRole=role)
