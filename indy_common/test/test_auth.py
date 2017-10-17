import pytest
from plenum.common.constants import VERKEY, STEWARD, SERVICES, NODE, TRUSTEE, NODE_IP, NODE_PORT, CLIENT_PORT, \
    CLIENT_IP, BLS_KEY, ALIAS

from indy_common.auth import Authoriser
from indy_common.constants import TRUST_ANCHOR, POOL_UPGRADE, ACTION, TGB


@pytest.fixture(scope='function', params=[STEWARD, TRUSTEE, TRUST_ANCHOR, None])
def role(request):
    return request.param


@pytest.fixture(scope='function', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(scope='function', params=[None, "value1"])
def old_values(request):
    return request.param


def test_node_enable(role, is_owner):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=SERVICES,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal="[VALIDATOR]",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_promote(role, is_owner):
    authorized = (role == STEWARD and is_owner) or (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=SERVICES,
                                               actorRole=role,
                                               oldVal="[]",
                                               newVal="[VALIDATOR]",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_demote(role, is_owner):
    authorized = (role == STEWARD and is_owner) or (role == TRUSTEE)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=SERVICES,
                                               actorRole=role,
                                               oldVal="[VALIDATOR]",
                                               newVal="[]",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_wrong_old_service_name(role, is_owner):
    assert not Authoriser.authorised(typ=NODE,
                                     field=SERVICES,
                                     actorRole=role,
                                     oldVal="aaa",
                                     newVal="[]",
                                     isActorOwnerOfSubject=is_owner)[0]


def test_node_wrong_new_service_name(role, is_owner):
    assert not Authoriser.authorised(typ=NODE,
                                     field=SERVICES,
                                     actorRole=role,
                                     oldVal="[]",
                                     newVal="aaa",
                                     isActorOwnerOfSubject=is_owner)[0]


def test_node_change_node_ip(role, is_owner, old_values):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=NODE_IP,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_change_node_port(role, is_owner, old_values):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=NODE_PORT,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_change_client_ip(role, is_owner, old_values):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=CLIENT_IP,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_change_client_port(role, is_owner, old_values):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=CLIENT_PORT,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_change_bls_keys(role, is_owner, old_values):
    authorized = (role == STEWARD and is_owner)
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=BLS_KEY,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_node_change_alias(role, is_owner, old_values):
    authorized = False  # alias can not be changed
    assert authorized == Authoriser.authorised(typ=NODE,
                                               field=ALIAS,
                                               actorRole=role,
                                               oldVal=old_values,
                                               newVal="value2",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_start(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal=None,
                                               newVal="start",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_cancel(role, is_owner):
    authorized = role in (TRUSTEE, TGB)
    assert authorized == Authoriser.authorised(typ=POOL_UPGRADE,
                                               field=ACTION,
                                               actorRole=role,
                                               oldVal="start",
                                               newVal="cancel",
                                               isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_old_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     field=ACTION,
                                     actorRole=role,
                                     oldVal="aaa",
                                     newVal="cancel",
                                     isActorOwnerOfSubject=is_owner)[0]


def test_pool_upgrade_wrong_new_name(role, is_owner):
    assert not Authoriser.authorised(typ=POOL_UPGRADE,
                                     field=ACTION,
                                     actorRole=role,
                                     oldVal="start",
                                     newVal="aaa",
                                     isActorOwnerOfSubject=is_owner)[0]
