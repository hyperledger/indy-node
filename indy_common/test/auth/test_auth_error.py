from plenum.common.constants import NODE, TRUSTEE, BLS_KEY, STEWARD

from indy_common.auth import Authoriser


def test_node_not_allowed_role_error():
    expected_msg = "TRUSTEE not in allowed roles ['STEWARD']"
    assert expected_msg == Authoriser.authorised(typ=NODE,
                                                 actorRole=TRUSTEE,
                                                 field=BLS_KEY,
                                                 oldVal=None,
                                                 newVal="some_value",
                                                 isActorOwnerOfSubject=False)[1]


def test_node_only_owner_error():
    expected_msg = "Only owner is allowed"
    assert expected_msg == Authoriser.authorised(typ=NODE,
                                                 actorRole=STEWARD,
                                                 field=BLS_KEY,
                                                 oldVal=None,
                                                 newVal="some_value",
                                                 isActorOwnerOfSubject=False)[1]
