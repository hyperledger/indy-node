import pytest
from indy_common.constants import SCHEMA

from indy_common.config_helper import NodeConfigHelper

from indy_node.persistence.idr_cache import IdrCache
from indy_node.test.request_handlers.helper import get_fake_ledger
from plenum.common.constants import KeyValueStorageType, DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.server.database_manager import DatabaseManager
from state.state import State
from storage.helper import initKeyValueStorage


@pytest.fixture(scope="module")
def db_manager(tconf, tdir):
    db_manager = DatabaseManager()
    name = 'name'
    idr_cache = IdrCache(name,
                         initKeyValueStorage(KeyValueStorageType.Rocksdb,
                                             tdir,
                                             tconf.idrCacheDbName,
                                             db_config=tconf.db_idr_cache_db_config))
    db_manager.register_new_store('idr', idr_cache)
    db_manager.register_new_database(DOMAIN_LEDGER_ID, get_fake_ledger(), State())
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
