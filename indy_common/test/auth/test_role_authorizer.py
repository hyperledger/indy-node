import pytest
import time

from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize.authorizer import RolesAuthorizer
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import CURRENT_PROTOCOL_VERSION, TARGET_NYM, TXN_TYPE, NYM
from plenum.test.helper import randomOperation
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope='module')
def req_auth():
    return Request(identifier="some_identifier",
                   reqId=1,
                   operation=randomOperation(),
                   signature="signature",
                   protocolVersion=CURRENT_PROTOCOL_VERSION)


@pytest.fixture(scope='module')
def idr_cache(req_auth):
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    cache.set(req_auth.identifier, 1, int(time.time()), role="SomeRole",
              verkey="SomeVerkey", isCommitted=False)
    return cache


@pytest.fixture(scope='module')
def idr_cache_none_role(req_auth):
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    cache.set(req_auth.identifier, 1, int(time.time()),
              verkey="SomeVerkey", isCommitted=False)
    return cache


def test_role_authorizer_get_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert authorizer.get_role(req_auth) == "SomeRole"


def test_role_authorizer_is_role_accepted(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert authorizer.is_role_accepted(req_auth, AuthConstraint(role="SomeRole", sig_count=1))


def test_role_authorizer_role_not_accepted(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert not authorizer.is_role_accepted(req_auth, AuthConstraint(role="SomeOtherRole", sig_count=1))


def test_role_authorizer_role_accepted_for_all_roles(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert authorizer.is_role_accepted(req_auth, AuthConstraint(role="*", sig_count=1))


def test_role_authorizer_is_owner_accepted(idr_cache, is_owner):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized = is_owner
    assert authorized == authorizer.is_owner_accepted(
        AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True),
        AuthActionAdd(txn_type=NYM, field='some_field', value='some_value', is_owner=is_owner))


def test_role_authorizer_authorize_with_owner(idr_cache, req_auth, is_owner):
    req = Request(identifier=req_auth.identifier,
                  operation={TARGET_NYM: req_auth.identifier,
                             TXN_TYPE: NYM},
                  signature='signature')
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req,
                                              AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True),
                                              AuthActionAdd(txn_type=NYM, field='some_field', value='some_value', is_owner=is_owner))
    assert authorized == is_owner


def test_role_authorizer_authorize_with_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role="SomeRole", sig_count=1))
    assert authorized


def test_role_authorizer_not_authorize_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role="SomeOtherRole", sig_count=1))
    assert not authorized
    assert reason == "Unknown role can not do this action"


def test_role_authorizer_not_authorize_unknown_nym(idr_cache):
    authorizer = RolesAuthorizer(cache=idr_cache)

    unknown_req_auth = Request(identifier="some_unknown_identifier",
                               reqId=2,
                               operation=randomOperation(),
                               signature="signature",
                               protocolVersion=CURRENT_PROTOCOL_VERSION)

    authorized, reason = authorizer.authorize(unknown_req_auth,
                                              AuthConstraint(role="SomeOtherRole", sig_count=1))
    assert not authorized
    assert reason == "sender's DID {} is not found in the Ledger".format(unknown_req_auth.identifier)


def test_role_authorizer_none_role_not_accepted(idr_cache_none_role, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache_none_role)
    assert not authorizer.is_role_accepted(req_auth, AuthConstraint(role="SomeRole", sig_count=1))


def test_role_authorizer_none_role_accepted_for_all_roles(idr_cache_none_role, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache_none_role)
    assert authorizer.is_role_accepted(req_auth, AuthConstraint(role="*", sig_count=1))


def test_role_authorizer_is_sig_count_accepted():
    """need to implementation"""
    pass


def test_role_authorizer_not_is_sig_count_accepted():
    """need to implementation"""
    pass


def test_role_authorizer_authorize_with_sig_count():
    """need to implementation"""
    pass


def test_role_authorizer_not_authorize_with_sig_count():
    """need to implementation"""
    pass
