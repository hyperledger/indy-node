from plenum.common.constants import TRUSTEE, STEWARD

from indy_common.auth import Authoriser
from indy_common.constants import REF, TGB, TRUST_ANCHOR, CLAIM_DEF


def test_claim_def_adding():
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, True)
        assert r and not msg


def test_claim_def_adding_without_permission():
    roles = {TGB, None}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, True)
        assert not r and msg


def test_claim_def_adding_not_owner():
    roles = {TRUSTEE, STEWARD, TRUST_ANCHOR}
    for role in roles:
        r, msg = _authorised_for_claim_def(role, False)
        assert not r and msg == "Only owner is allowed"


def test_claim_def_adding_with_some_field():
    r, msg = Authoriser.authorised(typ=CLAIM_DEF,
                                   actorRole=TRUSTEE,
                                   field="name",
                                   isActorOwnerOfSubject=True)
    assert r and not msg


def _authorised_for_claim_def(role, is_owner):
    return Authoriser.authorised(typ=CLAIM_DEF,
                                 actorRole=role,
                                 isActorOwnerOfSubject=is_owner)
