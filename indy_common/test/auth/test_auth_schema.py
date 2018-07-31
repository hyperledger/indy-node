from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser
from indy_common.constants import NAME, TGB, TRUST_ANCHOR, SCHEMA


def test_schema_adding(tconf):
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_schemas(role)
        assert r and not msg


def test_schema_adding_without_permission(tconf):
    roles = {TGB, None}
    for role in roles:
        r, msg = _authorised_for_schemas(role)
        assert not r and msg


def test_client_can_send_claim_def(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    r, msg = _authorised_for_schemas(None)
    assert r and not msg

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def test_client_cant_send_claim_def(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = True

    r, msg = _authorised_for_schemas(None)
    assert not r and "None role not in allowed roles" in msg

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def _authorised_for_schemas(role):
    return Authoriser.authorised(typ=SCHEMA,
                                 actorRole=role)
