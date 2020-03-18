import copy
import json
import random

import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_ID, RS_TYPE, RS_NAME, RS_VERSION, RS_CONTENT, ENDORSER, JSON_LD_ID_FIELD, \
    JSON_LD_TYPE_FIELD
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_pres_def_handler import \
    RichSchemaPresDefHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import context_request, make_rich_schema_object_exist
from plenum.common.constants import OP_VER, TRUSTEE
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import SortedDict, randomString


def test_update_state(handler_and_request):
    handler, request = handler_and_request
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    op = request.operation

    handler.update_state(txn, None, context_request)

    value = {
        'id': op[RS_ID],
        'rsType': op[RS_TYPE],
        'rsName': op[RS_NAME],
        'rsVersion': op[RS_VERSION],
        'content': op[RS_CONTENT],
        'from': request.identifier,
        'endorser': request.endorser,
        'ver': op[OP_VER],
    }
    primary_key = op[RS_ID]
    secondary_key = "{RS_TYPE}:{RS_NAME}:{RS_VERSION}".format(RS_TYPE=op['rsType'],
                                                              RS_NAME=op['rsName'],
                                                              RS_VERSION=op['rsVersion']).encode()

    value_from_state = handler.get_from_state(primary_key)
    assert SortedDict(value_from_state[0]) == SortedDict(value)
    assert value_from_state[1] == seq_no
    assert value_from_state[2] == txn_time
    assert handler.state.get(secondary_key, isCommitted=False) == op[RS_ID].encode()


def test_static_validation_pass(handler_and_request):
    handler, request = handler_and_request
    handler.static_validation(request)


def test_static_validation_content_is_json(handler_and_request):
    handler, request = handler_and_request

    request.operation[RS_CONTENT] = randomString()
    with pytest.raises(InvalidClientRequest, match="must be a JSON serialized string"):
        handler.static_validation(request)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_content_is_json_ld_with_atid(handler_and_request, status):
    handler, request = handler_and_request

    content = copy.deepcopy(json.loads(request.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_ID_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_ID_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_ID_FIELD] = None
    request.operation[RS_CONTENT] = json.dumps(content)

    if not isinstance(handler, (RichSchemaMappingHandler, RichSchemaHandler, RichSchemaPresDefHandler)):
        handler.static_validation(request)
        return

    with pytest.raises(InvalidClientRequest, match="'content' must be a valid JSON-LD and have non-empty '@id' field"):
        handler.static_validation(request)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_content_is_json_ld_with_attype(handler_and_request, status):
    handler, request = handler_and_request

    content = copy.deepcopy(json.loads(request.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(JSON_LD_TYPE_FIELD, None)
    elif status == 'empty':
        content[JSON_LD_TYPE_FIELD] = ""
    elif status == 'none':
        content[JSON_LD_TYPE_FIELD] = None
    request.operation[RS_CONTENT] = json.dumps(content)

    if not isinstance(handler, (RichSchemaMappingHandler, RichSchemaHandler, RichSchemaPresDefHandler)):
        handler.static_validation(request)
        return

    with pytest.raises(InvalidClientRequest,
                       match="'content' must be a valid JSON-LD and have non-empty '@type' field"):
        handler.static_validation(request)


def test_static_validation_atid_equals_to_id(handler_and_request):
    handler, request = handler_and_request

    content = copy.deepcopy(json.loads(request.operation[RS_CONTENT]))
    content["@id"] = request.operation[RS_ID] + "a"
    request.operation[RS_CONTENT] = json.dumps(content)
    if not isinstance(handler, (RichSchemaMappingHandler, RichSchemaHandler, RichSchemaPresDefHandler)):
        handler.static_validation(request)
        return

    with pytest.raises(InvalidClientRequest,
                       match="content's @id must be equal to id={}".format(request.operation[RS_ID])):
        handler.static_validation(request)


def test_dynamic_validation_failed_not_authorised(handler_and_request):
    handler, request = handler_and_request
    add_to_idr(handler.database_manager.idr_cache, request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        handler.dynamic_validation(request, 0)


def test_dynamic_validation_for_existing(handler_and_request):
    handler, request = handler_and_request
    make_rich_schema_object_exist(handler, request)
    add_to_idr(handler.database_manager.idr_cache, request.identifier, TRUSTEE)
    add_to_idr(handler.database_manager.idr_cache, request.endorser, ENDORSER)

    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        handler.dynamic_validation(request, 0)


def test_dynamic_validation_for_existing_metadata(handler_and_request):
    handler, request = handler_and_request
    make_rich_schema_object_exist(handler, request)
    add_to_idr(handler.database_manager.idr_cache, request.identifier, TRUSTEE)
    add_to_idr(handler.database_manager.idr_cache, request.endorser, ENDORSER)

    request.operation[RS_ID] = randomString()
    request.operation[RS_CONTENT] = randomString()
    request.reqId = random.randint(10, 1000000000)

    with pytest.raises(InvalidClientRequest,
                       match='An object with rsName="{}", rsVersion="{}" and rsType="{}" already exists. '
                             'Please choose different rsName, rsVersion or rsType'.format(
                           request.operation[RS_NAME], request.operation[RS_VERSION], request.operation[RS_TYPE])):
        handler.dynamic_validation(request, 0)
