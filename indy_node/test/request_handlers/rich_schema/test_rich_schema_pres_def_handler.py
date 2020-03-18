import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, JSON_LD_TYPE_FIELD, JSON_LD_ID_FIELD
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_pres_def_handler import \
    RichSchemaPresDefHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_pres_def_request
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def pres_def_req():
    return rich_schema_pres_def_request()


@pytest.fixture()
def pres_def_handler(db_manager, write_auth_req_validator):
    return RichSchemaPresDefHandler(db_manager, write_auth_req_validator)


def test_static_validation_pass(pres_def_handler, pres_def_req):
    pres_def_handler.static_validation(pres_def_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_id(pres_def_handler, pres_def_req, status):
    content = copy.deepcopy(json.loads(pres_def_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_ID_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_ID_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_ID_FIELD] = None
    pres_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@id' field"):
        pres_def_handler.static_validation(pres_def_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_type(pres_def_handler, pres_def_req, status):
    content = copy.deepcopy(json.loads(pres_def_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_TYPE_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_TYPE_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_TYPE_FIELD] = None
    pres_def_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@type' field"):
        pres_def_handler.static_validation(pres_def_req)


def test_schema_dynamic_validation_passes(pres_def_handler, pres_def_req):
    add_to_idr(pres_def_handler.database_manager.idr_cache, pres_def_req.identifier, TRUSTEE)
    add_to_idr(pres_def_handler.database_manager.idr_cache, pres_def_req.endorser, ENDORSER)
    pres_def_handler.dynamic_validation(pres_def_req, 0)
