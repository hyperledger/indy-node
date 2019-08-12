
import pytest
from indy_node.server.request_handlers.domain_req_handlers.context_handler import validate_data, validate_context, \
    ContextHandler
from plenum.common.request import Request
from indy_node.test.context.helper import W3C_BASE_CONTEXT, W3C_EXAMPLE_V1_CONTEXT


def test_validate_data_fail_on_empty():
    with pytest.raises(KeyError) as e:
        validate_data({})
    assert "name" in str(e.value)


def test_validate_data_fail_no_name():
    data = {
        "version": "2.5"
    }
    with pytest.raises(KeyError) as e:
        validate_data(data)
    assert "name" in str(e.value)


def test_validate_data_fail_no_version():
    data = {
        "name": "New Context"
    }
    with pytest.raises(KeyError) as e:
        validate_data(data)
    assert "version" in str(e.value)


def test_validate_data_fail_no_context():
    data = {
        "name": "New Context",
        "version": "5.2"
    }
    with pytest.raises(KeyError) as e:
        validate_data(data)
    assert "context" in str(e.value)


def test_validate_context_fail_on_empty():
    with pytest.raises(Exception) as e:
        validate_context({})
    assert "Context missing '@context' property" in str(e.value)


def test_validate_context_fail_not_dict():
    with pytest.raises(Exception) as e:
        validate_context("context")
    assert "context is not an object" in str(e.value)


def test_validate_context_fail_no_context_property():
    input_dict = {
        "name": "Thing"
    }
    with pytest.raises(Exception) as e:
        validate_context(input_dict)
    assert "Context missing '@context' property" in str(e.value)


@pytest.mark.skip("Until we find a string that fails the regex, or improve the test, this should be skipped")
def test_validate_context_fail_bad_uri():
    input_dict = {
        "@context": "2http:/..@#$"
    }
    with pytest.raises(Exception) as e:
        validate_context(input_dict)
    assert "fail" in str(e.value)


def test_validate_context_fail_context_not_uri_or_array_or_object():
    input_dict = {
        "@context": 52
    }
    with pytest.raises(Exception) as e:
        validate_context(input_dict)
    assert "'@context' value must be url, array, or object" in str(e.value)


def test_validate_context_pass_value_is_dict():
    input_dict = {
        "@context": {
            "favoriteColor": "https://example.com/vocab#favoriteColor"
        }
    }
    validate_context(input_dict)


def test_validate_context_pass_value_is_list():
    input_dict = {
        "@context": [
            {
                "favoriteColor": "https://example.com/vocab#favoriteColor"
            },
            "https://www.w3.org/ns/odrl.jsonld"
        ]
    }
    validate_context(input_dict)


def test_validate_context_pass_context_w3c_example_15():
    input_dict = {
        "@context": {
            "referenceNumber": "https://example.com/vocab#referenceNumber",
            "favoriteFood": "https://example.com/vocab#favoriteFood"
        }
    }
    validate_context(input_dict)


def test_static_validation_pass_valid_transaction():
    operation = {
        "data": {
            "name": "TestContext",
            "version": 1,
            "context_array": W3C_BASE_CONTEXT
        },
        "type": "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_validate_context_pass_context_w3c_base():
    # pasted directly out of the reference file, without any format changes
    # change true to True to correct for python
    # Sample from specification: https://w3c.github.io/vc-data-model/#base-context
    # Actual file contents from: https://www.w3.org/2018/credentials/v1
    validate_context(W3C_BASE_CONTEXT)


def test_static_validation_pass_valid_transaction():
    operation = {
        "data": {
            "name": "TestContext",
            "version": 1,
            "context": W3C_BASE_CONTEXT
        },
        "type": "200"
    }
    req = Request("test", 1, operation, "sig",)
    ch = ContextHandler(None, None)
    ch.static_validation(req)


def test_validate_context_pass_context_w3c_examples_v1():
    # test for https://www.w3.org/2018/credentials/examples/v1
    validate_context(W3C_EXAMPLE_V1_CONTEXT)





