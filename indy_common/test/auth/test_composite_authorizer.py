import pytest
import time

from indy_common.authorize.auth_constraints import AuthConstraint, \
    AuthConstraintAnd, \
    AuthConstraintOr, ConstraintsEnum
from indy_common.authorize.authorizer import CompositeAuthorizer, RolesAuthorizer, AndAuthorizer, OrAuthorizer, \
    AuthValidationError
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import CURRENT_PROTOCOL_VERSION, STEWARD, TRUSTEE
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
    cache.set(req_auth.identifier, 1, int(time.time()), role=STEWARD,
              verkey="SomeVerkey", isCommitted=False)
    return cache


@pytest.fixture(scope='module')
def composite_authorizer(idr_cache):
    authorizer = CompositeAuthorizer()
    authorizer.register_authorizer(RolesAuthorizer(idr_cache))
    authorizer.register_authorizer(AndAuthorizer(), ConstraintsEnum.AND_CONSTRAINT_ID)
    authorizer.register_authorizer(OrAuthorizer(), ConstraintsEnum.OR_CONSTRAINT_ID)
    return authorizer


@pytest.fixture(scope='module')
def other_req_id():
    return Request(identifier="some_other_identifier",
                   reqId=2,
                   operation=randomOperation(),
                   signature="signature",
                   protocolVersion=CURRENT_PROTOCOL_VERSION)


def test_authorize_with_role(composite_authorizer, req_auth):
    assert composite_authorizer.authorize(req_auth, AuthConstraint(STEWARD, 1), None)


def test_raise_on_not_authorize_with_other_role(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        assert composite_authorizer.authorize(req_auth, AuthConstraint(TRUSTEE, 1), None)


def test_authorize_with_and_constraint(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintAnd([AuthConstraint(STEWARD, 1), AuthConstraint(STEWARD, 1)]),
                                   None)


def test_not_authorize_with_and_constraint(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        composite_authorizer.authorize(req_auth,
                                       AuthConstraintAnd([AuthConstraint(STEWARD, 1), AuthConstraint(TRUSTEE, 1)]),
                                       None)


def test_authorize_with_or_constraint(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintOr([AuthConstraint(STEWARD, 1), AuthConstraint(STEWARD, 1)]),
                                   None)


def test_authorize_with_or_constraint_with_one_fail(composite_authorizer, req_auth):
    composite_authorizer.authorize(req_auth,
                                   AuthConstraintOr([AuthConstraint(STEWARD, 1), AuthConstraint(TRUSTEE, 1)]),
                                   None)


def test_not_authorized_with_or_constraint(composite_authorizer, req_auth):
    with pytest.raises(AuthValidationError):
        composite_authorizer.authorize(req_auth,
                                       AuthConstraintOr([AuthConstraint(TRUSTEE, 1), AuthConstraint(TRUSTEE, 1)]),
                                       None)
