import json

import pytest

from indy_common.constants import RS_CONTENT
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture()
def rich_schema_req():
    return rich_schema_request()


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


def test_static_validation_pass_complex(rich_schema_handler, rich_schema_req):
    rich_schema_handler.static_validation(rich_schema_req)


def test_static_validation_pass_simple(rich_schema_handler, rich_schema_req):
    rich_schema_req.operation[RS_CONTENT] = json.dumps({
        "@id": "some_id",
        "@type": "some_type",
        "aaa": "bbb"
    })
    rich_schema_handler.static_validation(rich_schema_req)


def test_static_validation_fail_no_id(rich_schema_handler, rich_schema_req):
    rich_schema_req.operation[RS_CONTENT] = json.dumps({
        "@type": "some_type",
        "aaa": "bbb"
    })
    with pytest.raises(InvalidClientRequest) as e:
        rich_schema_handler.static_validation(rich_schema_req)
    assert "Rich Schema must be a JSON-LD object and contain '@id' field in 'content'" in str(e.value)


def test_static_validation_fail_no_type(rich_schema_handler, rich_schema_req):
    rich_schema_req.operation[RS_CONTENT] = json.dumps({
        "@id": "some_id",
        "aaa": "bbb"
    })
    with pytest.raises(InvalidClientRequest) as e:
        rich_schema_handler.static_validation(rich_schema_req)
    assert "Rich Schema must be a JSON-LD object and contain '@type' field in 'content'" in str(e.value)
