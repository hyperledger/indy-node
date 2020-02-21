import random

import pytest
from indy_common.constants import REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, TAG

from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import KeyValueStorageType, TXN_TYPE, TXN_AUTHOR_AGREEMENT, TXN_AUTHOR_AGREEMENT_TEXT, \
    TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_RATIFICATION_TS
from plenum.common.request import Request
from plenum.common.util import randomString
from storage.helper import initKeyValueStorage
from indy_node.test.api.helper import req_id
_reqId = req_id()


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
                   operation={'type': "101",
                              'data': {
                                  'version': '1.0',
                                  'name': 'Degree',
                                  'attr_names': ['last_name',
                                                 'first_name', ]
                              }})





@pytest.fixture(scope="function")
def rs_schema_request():
    authors_did, name, version, _type = "2hoqvcwupRTUNkXn6ArYzs", randomString(), "1.1", "8"
    _id = authors_did + ':' + _type + ':' + name + ':' + version
    return Request(identifier=authors_did,
                   reqId=next(_reqId),
                   signature="sig",
                   protocolVersion=2,
                   operation={
                       "type": "201",
                       "meta": {
                           "type": "sch",
                           "name": name,
                           "version": version
                       },
                       "data": {
                           "schema": {
                               "@id": _id,
                               "@context": "ctx:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                               "@type": "rdfs:Class",
                               "rdfs:comment": "ISO18013 International Driver License",
                               "rdfs:label": "Driver License",
                               "rdfs:subClassOf": {
                                   "@id": "sch:Thing"
                               },
                               "driver": "Driver",
                               "dateOfIssue": "Date",
                               "dateOfExpiry": "Date",
                               "issuingAuthority": "Text",
                               "licenseNumber": "Text",
                               "categoriesOfVehicles": {
                                   "vehicleType": "Text",
                                   "vehicleType-input": {
                                       "@type": "sch:PropertyValueSpecification",
                                       "valuePattern": "^(A|B|C|D|BE|CE|DE|AM|A1|A2|B1|C1|D1|C1E|D1E)$"
                                   },
                                   "dateOfIssue": "Date",
                                   "dateOfExpiry": "Date",
                                   "restrictions": "Text",
                                   "restrictions-input": {
                                       "@type": "sch:PropertyValueSpecification",
                                       "valuePattern": "^([A-Z]|[1-9])$"
                                   }
                               },
                               "administrativeNumber": "Text"
                           }
                       }
                   })


@pytest.fixture(scope="function")
def rs_schema_broken_request():
    authors_did, name, version, _type = "2hoqvcwupRTUNkXn6ArYzs", randomString(), "1.1", "8"
    _id = authors_did + ':' + _type + ':' + name + ':' + version
    return Request(identifier=authors_did,
                   reqId=random.randint(1, 10000000000000000000),
                   signature="sig",
                   protocolVersion=2,
                   operation={'type': '201',
                              'data':
                                  {'schema':
                                       {'@id': '7MpRep22vL3bnyR8VqCvsS:8:ISO18023_Drivers_License:1.2',
                                        '@type': '0od'}
                                   },
                              'meta':
                                  {'type': 'sch',
                                   'version': '1.2',
                                   'name': 'ISO18023_Drivers_License'}
                              }
                   )





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
