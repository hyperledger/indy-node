import json

import pytest

from common.exceptions import LogicError
from indy_common.constants import RS_CONTENT, RS_ID, RS_NAME, RS_TYPE, RS_VERSION, JSON_LD_CONTEXT, \
    RS_CONTEXT_TYPE_VALUE, SET_JSON_LD_CONTEXT
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.json_ld_context_handler import \
    JsonLdContextHandler
from indy_node.test.context.helper import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT
from plenum.common.constants import TXN_TYPE, OP_VER
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request


@pytest.fixture()
def context_operation():
    return {
        TXN_TYPE: SET_JSON_LD_CONTEXT,
        OP_VER: '1.1',
        RS_ID: 'test_id',
        RS_NAME: 'testName',
        RS_TYPE: RS_CONTEXT_TYPE_VALUE,
        RS_VERSION: '1.0',
        RS_CONTENT: json.dumps({JSON_LD_CONTEXT: ['http://aaa.com']})
    }


def test_static_validation_context_fail_bad_uri(context_operation):
    context_operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT: 'http://aaa.com'})
    req = Request("test", 1, context_operation, "sig")

    ch = JsonLdContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)

    assert "@context URI 2http:/..@#$ badly formed" in str(e.value)


def test_static_validation_fail_context_not_uri_or_array_or_object(context_operation):
    context_operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT: 52})
    req = Request("test", 1, context_operation, "sig", )

    ch = JsonLdContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)

    assert "'@context' value must be url, array, or object" in str(e.value)


def test_static_validation_pass_context_value_is_dict(context_operation):
    context = {
        "favoriteColor": "https://example.com/vocab#favoriteColor"
    }
    context_operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT: context})
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_value_is_list_with_dict_and_uri(context_operation):
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "https://www.w3.org/ns/odrl.jsonld"
    ]
    context_operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT: context})
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_w3c_example_15(context_operation):
    context = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    context_operation[RS_CONTENT] = json.dumps(context)
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_fail_context_is_list_with_dict_and_bad_uri(context_operation):
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "this is a bad uri"
    ]
    context_operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT: context})
    req = Request("test", 1, context_operation, "sig", )

    ch = JsonLdContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)

    assert "@context URI this is a bad uri badly formed" in str(e.value)


def test_static_validation_pass_context_w3c_base(context_operation):
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    context_operation[RS_CONTENT] = json.dumps(W3C_BASE_CONTEXT)
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_w3c_examples_v1(context_operation):
    # test for https://www.w3.org/2018/credentials/examples/v1
    context_operation[RS_CONTENT] = json.dumps(W3C_EXAMPLE_V1_CONTEXT)
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_fail_invalid_type(context_operation):
    context_operation[RS_CONTENT] = json.dumps(W3C_BASE_CONTEXT)
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    with pytest.raises(LogicError):
        ch.static_validation(req)
