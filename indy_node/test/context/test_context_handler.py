
import pytest
from common.exceptions import LogicError
from indy_common.constants import CONTEXT_TYPE

from indy_node.server.request_handlers.domain_req_handlers.context_handler import validate_data, validate_context, \
    ContextHandler, validate_meta
from plenum.common.request import Request
from indy_node.test.context.helper import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT

def test_validate_meta_fail_on_empty():
    with pytest.raises(KeyError) as e:
        validate_meta({})
    assert "name" in str(e.value)


def test_validate_meta_fail_no_name():
    meta = {
        "version": "2.5"
    }
    with pytest.raises(KeyError) as e:
        validate_meta(meta)
    assert "name" in str(e.value)


def test_validate_meta_fail_no_version():
    meta = {
        "name": "New Context"
    }
    with pytest.raises(KeyError) as e:
        validate_meta(meta)
    assert "version" in str(e.value)


def test_validate_meta_fail_no_type():
    meta = {
        "name": "New Context",
        "version": "5.2"
    }
    with pytest.raises(KeyError) as e:
        validate_meta(meta)
    assert "type" in str(e.value)


def test_validate_meta_fail_wrong_type():
    meta = {
        "name": "New Context",
        "version": "5.2",
        "type": "sch"
    }
    with pytest.raises(Exception) as e:
        validate_meta(meta)
    assert "Context transaction meta 'type' is 'sch', should be 'ctx'" in str(e.value)


def test_validate_meta_pass():
    meta = {
        "name": "New Context",
        "version": "5.2",
        "type": "ctx"
    }
    validate_meta(meta)


def test_validate_data_fail_on_empty():
    with pytest.raises(Exception) as e:
        validate_data({})
    assert "data missing '@context' property" in str(e.value)


def test_validate_data_fail_not_dict():
    with pytest.raises(Exception) as e:
        validate_data("context")
    assert "data is not an object" in str(e.value)


def test_validate_data_fail_no_context_property():
    input_dict = {
        "name": "Thing"
    }
    with pytest.raises(Exception) as e:
        validate_data(input_dict)
    assert "data missing '@context' property" in str(e.value)


def test_validate_data_pass():
    validate_data({"@context": "https://www.example.com"})


def test_validate_context_fail_bad_uri():
    context = "2http:/..@#$"
    with pytest.raises(Exception) as e:
        validate_context(context)
    assert "2http:/..@#$" in str(e.value)


def test_validate_context_fail_context_not_uri_or_array_or_object():
    context = 52
    with pytest.raises(Exception) as e:
        validate_context(context)
    assert "'@context' value must be url, array, or object" in str(e.value)


def test_validate_context_pass_value_is_dict():
    context = {
        "favoriteColor": "https://example.com/vocab#favoriteColor"
    }
    validate_context(context)


def test_validate_context_pass_value_is_list_with_dict_and_uri():
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "https://www.w3.org/ns/odrl.jsonld"
    ]
    validate_context(context)


def test_validate_context_pass_context_w3c_example_15():
    input_dict = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    validate_context(input_dict)


def test_validate_context_fail_value_is_list_with_dict_and_bad_uri():
    context = [
        {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        },
        "this is a bad uri"
    ]
    with pytest.raises(Exception) as e:
        validate_context(context)
    assert "this is a bad uri" in str(e.value)


def test_validate_context_pass_context_w3c_base():
    # pasted directly out of the reference file, without any format changes
    # change true to True to correct for python
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    validate_context(W3C_BASE_CONTEXT)


def test_static_validation_pass_valid_transaction():
    operation = {
        "meta": {
            "name": "TestContext",
            "version": 1,
            "type": CONTEXT_TYPE
        },
        "data": W3C_BASE_CONTEXT,
        "type": "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_validate_context_pass_context_w3c_examples_v1():
    # test for https://www.w3.org/2018/credentials/examples/v1
    validate_context(W3C_EXAMPLE_V1_CONTEXT)


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


def test_static_validation_fail_no_meta():
    operation = {
        "data": W3C_BASE_CONTEXT,
        "type": "200"
    }
    req = Request("test", 1, operation, "sig", )
    ch = ContextHandler(None, None)
    with pytest.raises(KeyError) as e:
        ch.static_validation(req)
    assert 'meta' in str(e.value)


def test_static_validation_fail_no_data():
    operation = {
        "meta": {
            "type": CONTEXT_TYPE,
            "name": "TestContext",
            "version": 1
        },
        "type": "200"
    }
    req = Request("test", 1, operation, "sig", )
    ch = ContextHandler(None, None)
    with pytest.raises(KeyError) as e:
        ch.static_validation(req)
    assert "data" in str(e.value)


def test_static_validation_fail_no_type():
    operation = {
        "meta": {
            "type": CONTEXT_TYPE,
            "name": "TestContext",
            "version": 1
        },
        "data": W3C_BASE_CONTEXT
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    with pytest.raises(LogicError):
        ch.static_validation(req)
