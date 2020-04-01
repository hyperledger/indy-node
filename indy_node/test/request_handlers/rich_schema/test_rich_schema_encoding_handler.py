import copy
import json

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, RS_ENC_ALGORITHM
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_encoding_request
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def encoding_handler(db_manager, write_auth_req_validator):
    return RichSchemaEncodingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def encoding_req(encoding_handler):
    req = rich_schema_encoding_request()
    add_to_idr(encoding_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(encoding_handler.database_manager.idr_cache, req.endorser, ENDORSER)
    return req


@pytest.mark.parametrize('missing_field', ['input', 'output', 'algorithm', 'testVectors'])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_no_field(encoding_handler, encoding_req, missing_field, status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(missing_field, None)
    elif status == 'empty':
        content[missing_field] = {}
    elif status == 'none':
        content[missing_field] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be set in 'content'".format(missing_field)):
        encoding_handler.static_validation(encoding_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_no_all_fields(encoding_handler, encoding_req, status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop('input', None)
        content.pop('output', None)
        content.pop('algorithm', None)
        content.pop('testVectors', None)
    elif status == 'empty':
        content['input'] = {}
        content['output'] = {}
        content['algorithm'] = {}
        content['testVectors'] = {}
    elif status == 'none':
        content['input'] = None
        content['output'] = None
        content['algorithm'] = None
        content['testVectors'] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'input', 'output', 'algorithm', 'testVectors' must be set in 'content'"):
        encoding_handler.static_validation(encoding_req)


@pytest.mark.parametrize('missing_field', ['id', 'type'])
@pytest.mark.parametrize('input_output', ['input', 'output'])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_input_output(encoding_handler, encoding_req, missing_field, input_output, status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'missing':
        content[input_output].pop(missing_field, None)
    elif status == 'empty':
        content[input_output][missing_field] = {}
    elif status == 'none':
        content[input_output][missing_field] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be set in '{}'".format(missing_field, input_output)):
        encoding_handler.static_validation(encoding_req)


@pytest.mark.parametrize('input_output', ['input', 'output'])
@pytest.mark.parametrize('status', ['empty', 'none'])
def test_static_validation_input_output_all_missing(encoding_handler, encoding_req, input_output,
                                                    status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'empty':
        content[input_output]['id'] = {}
        content[input_output]['type'] = {}
    elif status == 'none':
        content[input_output]['id'] = None
        content[input_output]['type'] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'id' and 'type' must be set in '{}'".format(input_output)):
        encoding_handler.static_validation(encoding_req)


@pytest.mark.parametrize('missing_field', ['description', 'documentation', 'implementation'])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_algorithm(encoding_handler, encoding_req, missing_field, status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'missing':
        content[RS_ENC_ALGORITHM].pop(missing_field, None)
    elif status == 'empty':
        content[RS_ENC_ALGORITHM][missing_field] = {}
    elif status == 'none':
        content[RS_ENC_ALGORITHM][missing_field] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be set in '{}'".format(missing_field, RS_ENC_ALGORITHM)):
        encoding_handler.static_validation(encoding_req)


@pytest.mark.parametrize('status', ['empty', 'none'])
def test_static_validation_algorithm_all_missing(encoding_handler, encoding_req, status):
    content = copy.deepcopy(json.loads(encoding_req.operation[RS_CONTENT]))
    if status == 'empty':
        content[RS_ENC_ALGORITHM]['description'] = {}
        content[RS_ENC_ALGORITHM]['documentation'] = {}
        content[RS_ENC_ALGORITHM]['implementation'] = {}
    elif status == 'none':
        content[RS_ENC_ALGORITHM]['description'] = None
        content[RS_ENC_ALGORITHM]['documentation'] = None
        content[RS_ENC_ALGORITHM]['implementation'] = None
    encoding_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'description', 'documentation', 'implementation' must be set in '{}'".format(
                           RS_ENC_ALGORITHM)):
        encoding_handler.static_validation(encoding_req)


def test_dynamic_validation_passes(encoding_handler, encoding_req):
    encoding_handler.dynamic_validation(encoding_req, 0)
