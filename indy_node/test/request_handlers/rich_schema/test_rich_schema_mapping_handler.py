import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, JSON_LD_TYPE_FIELD, JSON_LD_ID_FIELD
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request, rich_schema_mapping_request
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def mapping_req():
    return rich_schema_mapping_request()


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


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


def test_schema_dynamic_validation_passes(mapping_handler, mapping_req):
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.identifier, TRUSTEE)
    add_to_idr(mapping_handler.database_manager.idr_cache, mapping_req.endorser, ENDORSER)
    mapping_handler.dynamic_validation(mapping_req, 0)
