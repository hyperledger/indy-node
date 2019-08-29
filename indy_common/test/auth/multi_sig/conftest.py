import pytest
import time

from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.constants import ENDORSER
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import TRUSTEE
from plenum.test.helper import randomOperation
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope='module')
def identity_owners():
    return ["identity_owners_{}".format(i) for i in range(5)]


@pytest.fixture(scope='module')
def trustees():
    return ["trustee_{}".format(i) for i in range(5)]


@pytest.fixture(scope='module')
def endorsers():
    return ["endorser_{}".format(i) for i in range(5)]


@pytest.fixture(scope='module')
def idr_cache(identity_owners, trustees, endorsers):
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    seq_no = 1
    for identifier in identity_owners:
        cache.set(identifier, seq_no, int(time.time()), role="",
                  verkey="owner_identifier_verkey", isCommitted=False)

    for identifier in trustees:
        cache.set(identifier, seq_no, int(time.time()), role=TRUSTEE,
                  verkey="trustee_identifier_verkey", isCommitted=False)
    for identifier in endorsers:
        cache.set(identifier, seq_no, int(time.time()), role=ENDORSER,
                  verkey="endorser_identifier_verkey", isCommitted=False)
    return cache


@pytest.fixture(scope='module')
def req(identity_owners):
    return Request(identifier=identity_owners[0],
                   operation=randomOperation())


@pytest.fixture(scope='module')
def key():
    return AuthActionAdd(txn_type='SomeType',
                         field='some_field',
                         value='new_value')
