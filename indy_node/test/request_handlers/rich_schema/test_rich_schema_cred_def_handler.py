import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, RS_ID, RS_CRED_DEF_SCHEMA, RS_CRED_DEF_MAPPING
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_cred_def_handler import \
    RichSchemaCredDefHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request, rich_schema_cred_def_request, \
    rich_schema_mapping_request, make_rich_schema_object_exist
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString


@pytest.fixture()
def cred_def_handler(db_manager, write_auth_req_validator):
    return RichSchemaCredDefHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req():
    return rich_schema_request()


@pytest.fixture()
def mapping_req():
    return rich_schema_mapping_request()


@pytest.fixture()
def cred_def_req(rich_schema_handler, mapping_handler, rich_schema_req, mapping_req):
    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)
    make_rich_schema_object_exist(mapping_handler, mapping_req)

    req = rich_schema_cred_def_request()

    content = copy.deepcopy(json.loads(req.operation[RS_CONTENT]))
    content[RS_CRED_DEF_SCHEMA] = rich_schema_req.operation[RS_ID]
    content[RS_CRED_DEF_MAPPING] = mapping_req.operation[RS_ID]
    req.operation[RS_CONTENT] = json.dumps(content)

    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.endorser, ENDORSER)

    return req


def test_static_validation_pass(cred_def_handler, cred_def_req):
    cred_def_handler.static_validation(cred_def_req)


@pytest.mark.parametrize('missing_field', ['signatureType', 'mapping', 'schema', 'publicKey'])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_no_field(cred_def_handler, cred_def_req, missing_field, status):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(missing_field, None)
    elif status == 'empty':
        content[missing_field] = ""
    elif status == 'none':
        content[missing_field] = None
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be set in 'content'".format(missing_field)):
        cred_def_handler.static_validation(cred_def_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_no_all_fields(cred_def_handler, cred_def_req, status):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop('signatureType', None)
        content.pop('mapping', None)
        content.pop('schema', None)
        content.pop('publicKey', None)
    elif status == 'empty':
        content['signatureType'] = ""
        content['mapping'] = ""
        content['schema'] = ""
        content['publicKey'] = ""
    elif status == 'none':
        content['signatureType'] = None
        content['mapping'] = None
        content['schema'] = None
        content['publicKey'] = None
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'signatureType', 'mapping', 'schema', 'publicKey' must be set in 'content'"):
        cred_def_handler.static_validation(cred_def_req)

def test_dynamic_validation_passes(cred_def_handler, cred_def_req):
    cred_def_handler.dynamic_validation(cred_def_req, 0)


@pytest.mark.parametrize('field', [RS_CRED_DEF_SCHEMA, RS_CRED_DEF_MAPPING])
def test_dynamic_validation_not_existent_ref(cred_def_handler, cred_def_req,
                                             field):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    wrong_id = randomString()
    content[field] = wrong_id
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="Can not find a referenced '{}' with id={}; please make sure that it has been added to the ledger".format(
                           field, wrong_id)):
        cred_def_handler.dynamic_validation(cred_def_req, 0)


def test_dynamic_validation_not_schema_in_schema_field(cred_def_handler, cred_def_req,
                                                       mapping_req):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    content[RS_CRED_DEF_SCHEMA] = mapping_req.operation[RS_ID]
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'schema' field must reference a schema with rsType=sch"):
        cred_def_handler.dynamic_validation(cred_def_req, 0)


def test_dynamic_validation_not_mapping_in_mapping_field(cred_def_handler, cred_def_req,
                                                         rich_schema_req):
    content = copy.deepcopy(json.loads(cred_def_req.operation[RS_CONTENT]))
    content[RS_CRED_DEF_MAPPING] = rich_schema_req.operation[RS_ID]
    cred_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'mapping' field must reference a mapping with rsType=map"):
        cred_def_handler.dynamic_validation(cred_def_req, 0)
