import pytest
import time

from indy_common.auth import Authoriser, generate_auth_map
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_map import authMap
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import STEWARD, TRUSTEE

from indy_common.constants import TRUST_ANCHOR
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.test.helper import randomOperation
from storage.kv_in_memory import KeyValueStorageInMemory


OTHER_IDENTIFIER = "some_other_identifier"


@pytest.fixture(scope='function', params=[STEWARD, TRUSTEE, TRUST_ANCHOR, None])
def role(request):
    return request.param


@pytest.fixture(scope='function', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(scope='function', params=[None, "value1"])
def old_values(request):
    return request.param


@pytest.fixture(scope='module')
def initialized_auth_map():
    Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles, False)


@pytest.fixture(scope='function')
def action_add():
    return AuthActionAdd(txn_type='SomeType',
                         field='some_field',
                         value='new_value')


@pytest.fixture(scope='function')
def action_edit():
    return AuthActionEdit(txn_type='SomeType',
                          field='some_field',
                          old_value='old_value',
                          new_value='new_value')


@pytest.fixture(scope='module')
def idr_cache():
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    cache.set("trustee_identifier", 1, int(time.time()), role=TRUSTEE,
              verkey="trustee_identifier_verkey", isCommitted=False)
    cache.set("steward_identifier", 2, int(time.time()), role=STEWARD,
              verkey="steward_identifier_verkey", isCommitted=False)
    cache.set("trust_anchor_identifier", 3, int(time.time()), role=TRUST_ANCHOR,
              verkey="trust_anchor_identifier_verkey", isCommitted=False)
    cache.set(OTHER_IDENTIFIER, 4, int(time.time()), role='OtherRole',
              verkey="other_verkey", isCommitted=False)
    return cache


@pytest.fixture(scope='module')
def write_auth_req_validator(idr_cache):
    validator = WriteRequestValidator(config={},
                                      auth_map=authMap,
                                      cache=idr_cache)
    return validator


@pytest.fixture(scope='module', params=["trustee_identifier", "steward_identifier", "trust_anchor_identifier"])
def identifier(request):
    return request.param


@pytest.fixture(scope='module')
def req(identifier):
    return Request(identifier=identifier,
                   operation=randomOperation(),
                   signature='signature')


@pytest.fixture(scope='module')
def write_request_validation(write_auth_req_validator):
    def wrapped(*args, **kwargs):
        try:
            write_auth_req_validator.validate(*args, **kwargs)
        except UnauthorizedClientRequest:
            return False
        return True
    return wrapped
