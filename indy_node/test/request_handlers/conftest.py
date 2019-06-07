import pytest
from indy_common.constants import SCHEMA

from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.request_handlers.helper import get_fake_ledger, add_to_idr
from indy_node.test.request_handlers.test_schema_handler import make_schema_exist
from plenum.common.constants import KeyValueStorageType, DOMAIN_LEDGER_ID, IDR_CACHE_LABEL
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.server.database_manager import DatabaseManager
from plenum.test.testing_utils import FakeSomething
from state.state import State
from storage.helper import initKeyValueStorage


@pytest.fixture(scope="module")
def db_manager(tconf, tdir):
    db_manager = DatabaseManager()

    state = State()
    state.txn_list = {}
    state.get = lambda key, isCommitted=True: state.txn_list.get(key, None)
    state.set = lambda key, value: state.txn_list.update({key: value})

    name = 'name'
    idr_cache = IdrCache(name,
                         initKeyValueStorage(KeyValueStorageType.Rocksdb,
                                             tdir,
                                             tconf.idrCacheDbName,
                                             db_config=tconf.db_idr_cache_db_config))
    db_manager.register_new_store(IDR_CACHE_LABEL, idr_cache)
    db_manager.register_new_database(DOMAIN_LEDGER_ID, get_fake_ledger(), state)
    return db_manager


@pytest.fixture(scope="function")
def schema_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   operation={'type': SCHEMA,
                              'data': {
                                  'version': '1.0',
                                  'name': 'Degree',
                                  'attr_names': ['last_name',
                                                 'first_name', ]
                              }})


@pytest.fixture(scope="module")
def schema_handler(db_manager):
    f = FakeSomething()
    make_schema_exist(f, False)
    return SchemaHandler(db_manager, f)


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier

