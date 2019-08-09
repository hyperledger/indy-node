import pytest
import time

from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.authorize.authorizer import RolesAuthorizer
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import CURRENT_PROTOCOL_VERSION, TARGET_NYM, TXN_TYPE, NYM, STEWARD, TRUSTEE
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
def req_multi_signed_by_non_author():
    return Request(identifier="some_identifier",
                   reqId=1,
                   operation=randomOperation(),
                   signatures={"some_identifier2": "sig"},
                   protocolVersion=CURRENT_PROTOCOL_VERSION)


@pytest.fixture(scope='module')
def idr_cache(req_auth):
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    cache.set(req_auth.identifier, 1, int(time.time()), role=STEWARD,
              verkey="SomeVerkey", isCommitted=False),
    cache.set("some_identifier2", 1, int(time.time()), role=STEWARD,
              verkey="SomeVerkey2", isCommitted=False)
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
    assert authorizer.get_role(req_auth) == STEWARD


def test_role_authorizer_is_role_accepted(idr_cache):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert authorizer.is_role_accepted(role="", auth_constraint_role=IDENTITY_OWNER)
    assert not authorizer.is_role_accepted(role=TRUSTEE, auth_constraint_role=IDENTITY_OWNER)
    assert not authorizer.is_role_accepted(role=None, auth_constraint_role=IDENTITY_OWNER)
    assert authorizer.is_role_accepted(role=TRUSTEE, auth_constraint_role=TRUSTEE)
    assert authorizer.is_role_accepted(role="", auth_constraint_role="*")


def test_role_authorizer_is_owner_accepted(idr_cache, is_owner):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized = is_owner
    assert authorized == authorizer.is_owner_accepted(
        AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=True),
        AuthActionAdd(txn_type=NYM, field='some_field', value='some_value', is_owner=is_owner))


def test_role_authorizer_authorize_with_owner(idr_cache, req_auth, is_owner):
    req = Request(identifier=req_auth.identifier,
                  operation={TARGET_NYM: req_auth.identifier,
                             TXN_TYPE: NYM},
                  signature='signature')
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req,
                                              AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=True),
                                              AuthActionAdd(txn_type=NYM, field='some_field', value='some_value',
                                                            is_owner=is_owner))
    assert authorized == is_owner


def test_role_authorizer_authorize_with_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role=STEWARD, sig_count=1))
    assert authorized


def test_role_authorizer_not_authorize_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role=TRUSTEE, sig_count=1))
    assert not authorized
    assert reason == "Not enough TRUSTEE signatures"


def test_role_authorizer_not_authorize_unknown_nym(idr_cache):
    authorizer = RolesAuthorizer(cache=idr_cache)

    unknown_req_auth = Request(identifier="some_unknown_identifier",
                               reqId=2,
                               operation=randomOperation(),
                               signature="signature",
                               protocolVersion=CURRENT_PROTOCOL_VERSION)

    authorized, reason = authorizer.authorize(unknown_req_auth,
                                              AuthConstraint(role=TRUSTEE, sig_count=1))
    assert not authorized
    assert reason == "sender's DID {} is not found in the Ledger".format(unknown_req_auth.identifier)


def test_role_authorizer_is_sig_count_accepted(idr_cache_none_role, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache_none_role)
    assert authorizer.is_sig_count_accepted(req_auth, AuthConstraint(role="*", sig_count=1))


def test_role_authorizer_not_is_sig_count_accepted(idr_cache_none_role, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache_none_role)
    assert not authorizer.is_sig_count_accepted(req_auth, AuthConstraint(role=TRUSTEE, sig_count=10))


def test_role_authorizer_off_ledger_signature_pass(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req_auth._identifier = 'id_off_ledger'
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role='*', sig_count=1,
                                                                       off_ledger_signature=True))
    assert authorized


def test_role_authorizer_off_ledger_signature_not_pass(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req_auth._identifier = 'id_off_ledger'
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role='*', sig_count=1,
                                                                       off_ledger_signature=False))
    assert not authorized
    assert "DID id_off_ledger is not found in the Ledger" in reason


def test_role_authorizer_off_ledger_signature_count_2_pass(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req_auth._identifier = 'id_off_ledger'
    req_auth.signature = None
    req_auth.signatures = {'id_off_ledger': 'signature', 'another_id_off_ledger': 'another_signature'}
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role='*', sig_count=2,
                                                                       off_ledger_signature=True))
    assert authorized


def test_role_authorizer_off_ledger_signature_count_2_different_pass(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req_auth.signature = None
    req_auth.signatures = {req_auth.identifier: 'signature', 'another_id_off_ledger': 'another_signature'}
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role='*', sig_count=2,
                                                                       off_ledger_signature=True))
    assert authorized


def test_role_authorizer_off_ledger_signature_count_0_pass(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req_auth._identifier = 'id_off_ledger'
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role='*', sig_count=0,
                                                                       off_ledger_signature=True))
    assert authorized


def test_signed_by_author_if_more_than_1_sig(idr_cache, req_multi_signed_by_non_author):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_multi_signed_by_non_author,
                                              AuthConstraint(role=STEWARD, sig_count=1))
    assert not authorized
    assert "Author must sign the transaction" in reason


def test_no_sign_by_author_if_0_sig(idr_cache, req_multi_signed_by_non_author):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_multi_signed_by_non_author,
                                              AuthConstraint(role=STEWARD, sig_count=0))
    assert authorized
