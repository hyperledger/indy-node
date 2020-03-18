import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, JSON_LD_ID_FIELD, JSON_LD_TYPE_FIELD
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def rich_schema_req():
    return rich_schema_request()


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


def test_static_validation_pass(rich_schema_handler, rich_schema_req):
    rich_schema_handler.static_validation(rich_schema_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_id(rich_schema_handler, rich_schema_req, status):
    content = copy.deepcopy(json.loads(rich_schema_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_ID_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_ID_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_ID_FIELD] = None
    rich_schema_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@id' field"):
        rich_schema_handler.static_validation(rich_schema_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_type(rich_schema_handler, rich_schema_req, status):
    content = copy.deepcopy(json.loads(rich_schema_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_TYPE_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_TYPE_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_TYPE_FIELD] = None
    rich_schema_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@type' field"):
        rich_schema_handler.static_validation(rich_schema_req)


def test_schema_dynamic_validation_passes(rich_schema_handler, rich_schema_req):
    add_to_idr(rich_schema_handler.database_manager.idr_cache, rich_schema_req.identifier, TRUSTEE)
    add_to_idr(rich_schema_handler.database_manager.idr_cache, rich_schema_req.endorser, ENDORSER)
    rich_schema_handler.dynamic_validation(rich_schema_req, 0)
