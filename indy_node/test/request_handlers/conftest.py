import pytest
from indy_common.config_helper import NodeConfigHelper

from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import KeyValueStorageType

from plenum.server.database_manager import DatabaseManager
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
    return db_manager
