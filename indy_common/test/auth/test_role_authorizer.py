from indy_common.auth_constraints import AuthConstraint
from indy_common.authorizer import RolesAuthorizer
from indy_common.types import Request
from plenum.common.constants import CURRENT_PROTOCOL_VERSION
from plenum.test.helper import randomOperation


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


def test_role_authorizer_is_owner_accepted(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    assert authorizer.is_owner_accepted(req_auth, AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True))


def test_role_authorizer_is_owner_not_accepted(idr_cache):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req = Request(identifier="some_other_identifier",
                  reqId=2,
                  operation=randomOperation(),
                  signature="signature",
                  protocolVersion=CURRENT_PROTOCOL_VERSION)
    assert not authorizer.is_owner_accepted(req, AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True))


def test_role_authorizer_authorize_with_owner(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True))
    assert authorized


def test_role_authorizer_not_authorize_with_owner(idr_cache):
    authorizer = RolesAuthorizer(cache=idr_cache)
    req = Request(identifier="some_other_identifier",
                  reqId=2,
                  operation=randomOperation(),
                  signature="signature",
                  protocolVersion=CURRENT_PROTOCOL_VERSION)
    authorized, reason = authorizer.authorize(req, AuthConstraint(role="SomeRole", sig_count=1, need_to_be_owner=True))
    assert not authorized


def test_role_authorizer_authorize_with_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role="SomeRole", sig_count=1))
    assert authorized


def test_role_authorizer_not_authorize_role(idr_cache, req_auth):
    authorizer = RolesAuthorizer(cache=idr_cache)
    authorized, reason = authorizer.authorize(req_auth, AuthConstraint(role="SomeOtherRole", sig_count=1))
    assert not authorized
    assert reason == "role is not accepted"


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
