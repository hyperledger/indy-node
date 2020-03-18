import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, JSON_LD_TYPE_FIELD, JSON_LD_ID_FIELD, RS_MAPPING_SCHEMA, RS_ID
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request, rich_schema_mapping_request, \
    rich_schema_encoding_request, make_rich_schema_object_exist
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString


@pytest.fixture()
def mapping_req():
    return rich_schema_mapping_request()


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def encoding_req():
    return rich_schema_encoding_request()


@pytest.fixture()
def encoding_handler(db_manager, write_auth_req_validator):
    return RichSchemaEncodingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req():
    return rich_schema_request()


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


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


TEST_MAPPING = {
    '@id': "did:sov:8a9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@context': "did:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@type': "rdfs:Class",
    "schema": "did:sov:4e9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    "driver": [{
        "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
        "rank": 5
    }],
    "dateOfIssue": [{
        "enc": "did:sov:2x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
        "rank": 4
    }]
}


def test_schema_dynamic_validation_passes(mapping_handler, mapping_req,
                                          encoding_handler, encoding_req,
                                          rich_schema_handler, rich_schema_req):
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.identifier, TRUSTEE)
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.endorser, ENDORSER)

    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)

    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = rich_schema_req.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_existent_schema(mapping_handler, mapping_req,
                                                encoding_handler, encoding_req,
                                                rich_schema_handler, rich_schema_req):
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.identifier, TRUSTEE)
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.endorser, ENDORSER)

    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)

    schema_id = randomString()
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = schema_id
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match='Can not find a schema with id={}; please make sure that it has been added to the ledger'.format(
                           schema_id)):
        mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_schema_in_schema_field(mapping_handler, mapping_req,
                                                       encoding_handler, encoding_req,
                                                       rich_schema_handler, rich_schema_req):
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.identifier, TRUSTEE)
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.endorser, ENDORSER)

    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)
    make_rich_schema_object_exist(encoding_handler, encoding_req)

    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = encoding_req.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'schema' field must reference a schema with rsType=sch"):
        mapping_handler.dynamic_validation(mapping_req, 0)
