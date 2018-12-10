import pytest

from indy_common.auth_constraints import AuthConstraint, AND_CONSTRAINT_ID, OR_CONSTRAINT_ID, AuthConstraintAnd, \
    AuthConstraintOr
from indy_common.authorizer import CompositeAuthorizer, RolesAuthorizer, AndAuthorizer, OrAuthorizer, \
    AuthValidationError
from indy_common.types import Request
from plenum.common.constants import CURRENT_PROTOCOL_VERSION
from plenum.test.helper import randomOperation


@pytest.fixture(scope='module')
def composite_authorizer(idr_cache):
    authorizer = CompositeAuthorizer()
    authorizer.register_authorizer(RolesAuthorizer(idr_cache))
    authorizer.register_authorizer(AndAuthorizer(), AND_CONSTRAINT_ID)
    authorizer.register_authorizer(OrAuthorizer(), OR_CONSTRAINT_ID)
    return authorizer


@pytest.fixture(scope='module')
def other_req_id():
    return Request(identifier="some_other_identifier",
                   reqId=2,
                   operation=randomOperation(),
                   signature="signature",
                   protocolVersion=CURRENT_PROTOCOL_VERSION)


def test_authorize_with_role(composite_authorizer, req_auth):
    assert composite_authorizer.authorize(req_auth, AuthConstraint("SomeRole", 1), None)


def test_raise_on_not_authorize_with_other_role(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        assert composite_authorizer.authorize(req_auth, AuthConstraint("SomeOtherRole", 1), None)


def test_authorize_with_and_constraint(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintAnd([AuthConstraint("SomeRole", 1), AuthConstraint("SomeRole", 1)]),
                                   None)


def test_not_authorize_with_and_constraint(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        composite_authorizer.authorize(req_auth,
                                       AuthConstraintAnd([AuthConstraint("SomeRole", 1), AuthConstraint("SomeOtherRole", 1)]),
                                       None)


def test_authorize_with_or_constraint(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintOr([AuthConstraint("SomeRole", 1), AuthConstraint("SomeRole", 1)]),
                                   None)


def test_authorize_with_or_constraint_with_one_fail(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintOr([AuthConstraint("SomeRole", 1), AuthConstraint("SomeOtherRole", 1)]),
                                   None)


def test_not_authorized_with_or_constraint(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        composite_authorizer.authorize(req_auth,
                                       AuthConstraintOr([AuthConstraint("SomeOtherRole", 1), AuthConstraint("SomeOtherRole", 1)]),
                                       None)
