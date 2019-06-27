import pytest
from indy_common.constants import SCHEMA, CONFIG_LEDGER_ID, REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, TAG

from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.request_handlers.helper import get_fake_ledger, add_to_idr
from indy_node.test.request_handlers.test_schema_handler import make_schema_exist
from plenum.common.constants import KeyValueStorageType, DOMAIN_LEDGER_ID, IDR_CACHE_LABEL, POOL_LEDGER_ID
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.server.database_manager import DatabaseManager
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from state.state import State
from storage.helper import initKeyValueStorage
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope="module")
def idr_cache(tconf, tdir):
    name = 'name'
    idr_cache = IdrCache(name,
                         initKeyValueStorage(KeyValueStorageType.Rocksdb,
                                             tdir,
                                             tconf.idrCacheDbName,
                                             db_config=tconf.db_idr_cache_db_config))
    return idr_cache


@pytest.fixture(scope="module")
def schema_handler(db_manager, write_auth_req_validator):
    return SchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="module")
def db_manager(tconf, tdir, idr_cache):
    db_manager = DatabaseManager()

    db_manager.register_new_store(IDR_CACHE_LABEL, idr_cache)
    db_manager.register_new_database(DOMAIN_LEDGER_ID, get_fake_ledger(),
                                     PruningState(KeyValueStorageInMemory()))
    db_manager.register_new_database(CONFIG_LEDGER_ID, get_fake_ledger(),
                                     PruningState(KeyValueStorageInMemory()))
    db_manager.register_new_database(POOL_LEDGER_ID, get_fake_ledger(),
                                     PruningState(KeyValueStorageInMemory()))
    return db_manager


@pytest.fixture(scope="function")
def schema_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   signature="sig",
                   operation={'type': SCHEMA,
                              'data': {
                                  'version': '1.0',
                                  'name': 'Degree',
                                  'attr_names': ['last_name',
                                                 'first_name', ]
                              }})


@pytest.fixture(scope="module")
def revoc_reg_def_handler(db_manager, write_auth_req_validator):
    return RevocRegDefHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="module")
def revoc_reg_def_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   signature="sig",
                   operation={'type': REVOC_REG_DEF,
                              CRED_DEF_ID: "credDefId",
                              REVOC_TYPE: randomString(),
                              TAG: randomString(),
                              })


@pytest.fixture(scope="module")
def creator(db_manager):
    identifier = randomString()
    idr = db_manager.idr_cache
    add_to_idr(idr, identifier, None)
    return identifier

