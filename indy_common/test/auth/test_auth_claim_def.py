from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser
from indy_common.constants import REF, TGB, TRUST_ANCHOR, CLAIM_DEF


def test_claim_def_adding(tconf):
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, True)
        assert r and not msg


def test_claim_def_adding_without_permission(tconf):
    roles = {TGB, None}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, True)
        assert not r and msg


def test_claim_def_adding_not_owner(tconf):
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, False)
        assert not r and msg == "Only owner is allowed"


def test_claim_def_adding_with_some_field(tconf):
    r, msg = Authoriser.authorised(typ=CLAIM_DEF,
                                   actorRole=TRUSTEE,
                                   field="name",
                                   isActorOwnerOfSubject=True)
    assert r and not msg


def test_client_can_send_claim_def(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    r, msg = Authoriser.authorised(typ=CLAIM_DEF,
                                   actorRole=None,
                                   field="name",
                                   isActorOwnerOfSubject=True)
    assert r and not msg

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def test_client_cant_send_claim_def(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = True

    r, msg = Authoriser.authorised(typ=CLAIM_DEF,
                                   actorRole=None,
                                   field="name",
                                   isActorOwnerOfSubject=True)
    assert not r and "None role not in allowed roles" in msg

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def _authorised_for_claim_def(role, is_owner):
    return Authoriser.authorised(typ=CLAIM_DEF,
                                 actorRole=role,
                                 isActorOwnerOfSubject=is_owner)
