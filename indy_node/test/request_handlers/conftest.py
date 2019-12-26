import pytest
from indy_common.constants import SCHEMA, REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, TAG, CONTEXT_TYPE

from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.request_handlers.domain_req_handlers.context_handler import ContextHandler
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from indy_node.test.context.helper import W3C_BASE_CONTEXT
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import KeyValueStorageType, TXN_TYPE, TXN_AUTHOR_AGREEMENT, TXN_AUTHOR_AGREEMENT_TEXT, \
    TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_RATIFICATION_TS
from plenum.common.request import Request
from plenum.common.util import randomString
from storage.helper import initKeyValueStorage


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
def context_handler(db_manager, write_auth_req_validator):
    return ContextHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def context_request():
    return Request(identifier=randomString(),
                   reqId=1234,
                   signature="sig",
                   operation={
                       "meta": {
                           "type": CONTEXT_TYPE,
                           "name": "TestContext",
                           "version": 1
                       },
                       "data": W3C_BASE_CONTEXT,
                       "type": "200"
                   })


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


@pytest.fixture(scope="function")
def auth_rule_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   signature="sig",
                   operation=generate_auth_rule_operation())


@pytest.fixture(scope="module")
def taa_request(creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: TXN_AUTHOR_AGREEMENT,
                              TXN_AUTHOR_AGREEMENT_TEXT: "text",
                              TXN_AUTHOR_AGREEMENT_VERSION: "version",
                              TXN_AUTHOR_AGREEMENT_RATIFICATION_TS: 0})
