import json

import pytest

from common.exceptions import LogicError
from indy_common.constants import RS_CONTENT, JSON_LD_CONTEXT_FIELD, ENDORSER
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.json_ld_context_handler import \
    JsonLdContextHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import context_request
from indy_node.test.rich_schema.templates import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT
from plenum.common.constants import TXN_TYPE, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def context_handler(db_manager, write_auth_req_validator):
    return JsonLdContextHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def context_req(context_handler):
    req = context_request()
    add_to_idr(context_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(context_handler.database_manager.idr_cache, req.endorser, ENDORSER)
    return req


def test_static_validation_context_no_context_field(context_handler, context_req):
    context_req.operation[RS_CONTENT] = json.dumps({"aaa": "2http:/..@#$"})
    with pytest.raises(InvalidClientRequest) as e:
        context_handler.static_validation(context_req)

    assert "must contain a @context field" in str(e.value)


def test_static_validation_context_fail_bad_uri(context_handler, context_req):
    context_req.operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT_FIELD: "2http:/..@#$"})
    with pytest.raises(InvalidClientRequest) as e:
        context_handler.static_validation(context_req)

    assert "@context URI 2http:/..@#$ badly formed" in str(e.value)


def test_static_validation_fail_context_not_uri_or_array_or_object(context_handler, context_req):
    context_req.operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT_FIELD: 52})
    with pytest.raises(InvalidClientRequest) as e:
        context_handler.static_validation(context_req)

    assert "'@context' value must be url, array, or object" in str(e.value)


def test_static_validation_pass_context_value_is_dict(context_handler, context_req):
    context = {
        "favoriteColor": "https://example.com/vocab#favoriteColor"
    }
    context_req.operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT_FIELD: context})
    context_handler.static_validation(context_req)


def test_static_validation_pass_context_value_is_list_with_dict_and_uri(context_handler, context_req):
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "https://www.w3.org/ns/odrl.jsonld"
    ]
    context_req.operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT_FIELD: context})
    context_handler.static_validation(context_req)


def test_static_validation_pass_context_w3c_example_15(context_handler, context_req):
    context = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    context_req.operation[RS_CONTENT] = json.dumps(context)
    context_handler.static_validation(context_req)


def test_static_validation_fail_context_is_list_with_dict_and_bad_uri(context_handler, context_req):
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "this is a bad uri"
    ]
    context_req.operation[RS_CONTENT] = json.dumps({JSON_LD_CONTEXT_FIELD: context})
    with pytest.raises(InvalidClientRequest) as e:
        context_handler.static_validation(context_req)

    assert "@context URI this is a bad uri badly formed" in str(e.value)


def test_static_validation_pass_context_w3c_base(context_handler, context_req):
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    context_req.operation[RS_CONTENT] = json.dumps(W3C_BASE_CONTEXT)
    context_handler.static_validation(context_req)


def test_static_validation_pass_context_w3c_examples_v1(context_handler, context_req):
    # test for https://www.w3.org/2018/credentials/examples/v1
    context_req.operation[RS_CONTENT] = json.dumps(W3C_EXAMPLE_V1_CONTEXT)
    context_handler.static_validation(context_req)


def test_static_validation_fail_invalid_type(context_handler, context_req):
    context_req.operation[TXN_TYPE] = "201"
    with pytest.raises(LogicError):
        context_handler.static_validation(context_req)


def test_schema_dynamic_validation_passes(context_handler, context_req):
    context_handler.dynamic_validation(context_req, 0)
