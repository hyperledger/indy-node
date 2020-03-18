import copy
import json
from functools import reduce
from operator import getitem

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, JSON_LD_TYPE_FIELD, JSON_LD_ID_FIELD, RS_MAPPING_SCHEMA, RS_ID, \
    RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA, \
    RS_SCHEMA_TYPE_VALUE
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import make_rich_schema_object_exist, rs_req
from indy_node.test.rich_schema.templates import RICH_SCHEMA_ENCODING_EX1, RICH_SCHEMA_EX1
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString

TEST_MAPPING = {
    '@id': "did:sov:8a9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@context': "did:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@type': "rdfs:Class",
    "schema": "did:sov:4e9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    "attr1": [
        {
            "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
            "rank": 3
        }
    ],
    "attr2": [
        {
            "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
            "rank": 2
        },
        {
            "enc": "did:sov:2x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
            "rank": 1
        },
    ],
    "attr3": {
        "attr4": {
            "attr5": [
                {
                    "enc": "did:sov:3x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                    "rank": 4
                }
            ]
        }
    }
}

TEST_ENCODING_1 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")

TEST_ENCODING_2 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:2x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")

TEST_ENCODING_3 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:3x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def encoding_handler(db_manager, write_auth_req_validator):
    return RichSchemaEncodingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req():
    id = "did:sov:4e9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD"
    content = copy.deepcopy(RICH_SCHEMA_EX1)
    content['@id'] = id
    return rs_req(RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE,
                  content=content, id=id)


@pytest.fixture()
def mapping_req(rich_schema_handler, encoding_handler, rich_schema_req):
    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_1)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_2)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_3)

    id = randomString()
    content = copy.deepcopy(TEST_MAPPING)
    content['@id'] = id
    req = rs_req(RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE,
                 content=content, id=id)

    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.endorser, ENDORSER)

    return req


def test_static_validation_pass(mapping_handler, mapping_req):
    mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_id(mapping_handler, mapping_req, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_ID_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_ID_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_ID_FIELD] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@id' field"):
        mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_type(mapping_handler, mapping_req, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_TYPE_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_TYPE_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_TYPE_FIELD] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@type' field"):
        mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_schema(mapping_handler, mapping_req, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(RS_MAPPING_SCHEMA, None)
    elif status == 'empty':
        content[RS_MAPPING_SCHEMA] = ""
    elif status == 'none':
        content[RS_MAPPING_SCHEMA] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="schema must be set in content"):
        mapping_handler.static_validation(mapping_req)


def test_schema_dynamic_validation_passes(mapping_handler, mapping_req):
    mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_existent_schema(mapping_handler, mapping_req):
    schema_id = randomString()
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = schema_id
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match='Can not find a schema with id={}; please make sure that it has been added to the ledger'.format(
                           schema_id)):
        mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_schema_in_schema_field(mapping_handler, mapping_req):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = TEST_ENCODING_1.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'schema' field must reference a schema with rsType=sch"):
        mapping_handler.dynamic_validation(mapping_req, 0)


def get_mapping_attr_value(keys, mapping_content):
    return reduce(getitem, keys, mapping_content)


@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 'attr5'], 0)
])
def test_dynamic_validation_not_existent_encoding(mapping_handler, mapping_req,
                                                  enc_path, index):
    enc_id = randomString()
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    get_mapping_attr_value(enc_path, content)[index][RS_ENCODING_TYPE_VALUE] = enc_id
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="Can not find a referenced encoding with id={} in '{}' attribute; please make sure that it has been added to the ledger".format(
                           enc_id, enc_path[-1])):
        mapping_handler.dynamic_validation(mapping_req, 0)


@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 'attr5'], 0)
])
def test_dynamic_validation_not_encoding_in_enc_field(mapping_handler, mapping_req,
                                                      rich_schema_req,
                                                      enc_path, index):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    get_mapping_attr_value(enc_path, content)[RS_ENCODING_TYPE_VALUE] = rich_schema_req.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'enc' field in '{}' attribute must reference an encoding with rsType=enc"):
        mapping_handler.dynamic_validation(mapping_req, 0)
