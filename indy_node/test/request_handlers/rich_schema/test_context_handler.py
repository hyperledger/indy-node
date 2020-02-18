import json

import pytest

from common.exceptions import LogicError
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_CONTENT, RS_ID, RS_NAME, RS_TYPE, RS_VERSION, JSON_LD_CONTEXT, \
    RS_CONTEXT_TYPE_VALUE, SET_JSON_LD_CONTEXT
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.json_ld_context_handler import \
    JsonLdContextHandler
from indy_node.test.context.helper import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import DATA, TRUSTEE, TXN_TYPE, OP_VER
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, reqToTxn, append_txn_metadata
from plenum.server.request_handlers.utils import encode_state_value


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


def make_context_exist(context_request, context_handler):
    identifier, req_id, operation = get_request_data(context_request)
    context_name = get_write_context_name(context_request)
    context_version = get_write_context_version(context_request)
    path = ContextHandler.make_state_path_for_context(identifier, context_name, context_version)
    context_handler.state.set(path, encode_state_value("value", "seqNo", "txnTime"))


def test_context_dynamic_validation_failed_existing_context(context_request, context_handler):
    make_context_exist(context_request, context_handler)
    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        context_handler.dynamic_validation(context_request, 0)


def test_context_dynamic_validation_failed_not_authorised(context_request, context_handler):
    add_to_idr(context_handler.database_manager.idr_cache, context_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        context_handler.dynamic_validation(context_request, 0)


def test_schema_dynamic_validation_passes(context_request, context_handler):
    add_to_idr(context_handler.database_manager.idr_cache, context_request.identifier, TRUSTEE)
    context_handler.dynamic_validation(context_request, 0)


def test_update_state(context_request, context_handler):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(context_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path, value_bytes = ContextHandler.prepare_context_for_state(txn)
    value = {
        META: get_txn_context_meta(txn),
        DATA: get_txn_context_data(txn)
    }

    context_handler.update_state(txn, None, context_request)
    assert context_handler.get_from_state(path) == (value, seq_no, txn_time)
