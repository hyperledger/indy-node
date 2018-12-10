import pytest
import time

from indy_common.auth import Authoriser, generate_auth_map
from indy_common.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import STEWARD, TRUSTEE, CURRENT_PROTOCOL_VERSION

from indy_common.constants import TRUST_ANCHOR
from plenum.test.helper import randomOperation
from storage.kv_in_memory import KeyValueStorageInMemory


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
    cache.set(req_auth.identifier, 1, int(time.time()), role="SomeRole", verkey="SomeVerkey", isCommitted=False)
    return cache
