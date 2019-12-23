
import pytest

from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import DATA, TRUSTEE

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest

from indy_common.req_utils import get_write_context_name, get_write_context_version, get_txn_context_meta, \
    get_txn_context_data
from plenum.common.txn_util import get_request_data, reqToTxn, append_txn_metadata

from common.exceptions import LogicError
from indy_common.constants import CONTEXT_TYPE, META, RS_TYPE, CONTEXT_CONTEXT

from indy_node.server.request_handlers.domain_req_handlers.context_handler import ContextHandler
from plenum.common.request import Request
from indy_node.test.context.helper import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT
from plenum.server.request_handlers.utils import encode_state_value


def test_static_validation_context_fail_bad_uri():
    context = "2http:/..@#$"
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)
    assert "@context URI 2http:/..@#$ badly formed" in str(e.value)


def test_static_validation_fail_context_not_uri_or_array_or_object():
    context = 52
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)
    assert "'@context' value must be url, array, or object" in str(e.value)


def test_static_validation_pass_context_value_is_dict():
    context = {
        "favoriteColor": "https://example.com/vocab#favoriteColor"
    }
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_value_is_list_with_dict_and_uri():
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "https://www.w3.org/ns/odrl.jsonld"
    ]
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_w3c_example_15():
    context = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_fail_context_is_list_with_dict_and_bad_uri():
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "this is a bad uri"
    ]
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: context
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    with pytest.raises(InvalidClientRequest) as e:
        ch.static_validation(req)
    assert "@context URI this is a bad uri badly formed" in str(e.value)


def test_static_validation_pass_context_w3c_base():
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: W3C_BASE_CONTEXT
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_pass_context_w3c_examples_v1():
    # test for https://www.w3.org/2018/credentials/examples/v1
    operation = {
        META: {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        DATA: {
            CONTEXT_CONTEXT: W3C_EXAMPLE_V1_CONTEXT
        },
        RS_TYPE: "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_static_validation_fail_invalid_type():
    operation = {
        "meta": {
            "type": "context",
            "name": "TestContext",
            "version": 1
        },
        "data": W3C_BASE_CONTEXT,
        "type": "201"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    with pytest.raises(LogicError):
        ch.static_validation(req)


def test_static_validation_fail_no_type(context_handler, context_request):
    del context_request.operation['type']
    with pytest.raises(LogicError):
        context_handler.static_validation(context_request)


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

