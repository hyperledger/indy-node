from functools import partial

import pytest
from indy_common.constants import SCHEMA, GET_SCHEMA

from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.server.request_handlers.read_req_handlers.get_schema_handler import GetSchemaHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def schema_handler(db_manager):
    f = FakeSomething()
    make_schema_exist(f, False)
    return SchemaHandler(db_manager, f)


def make_schema_exist(handler, is_exist: bool):
    def exist(author, schemaName, schemaVersion, with_proof):
        return is_exist, None, None, None

    handler.getSchema = exist


def test_schema_dynamic_validation_failed_existing_schema(schema_request, schema_handler):
    make_schema_exist(schema_handler.get_schema_handler, True)
    with pytest.raises(InvalidClientRequest):
        schema_handler.dynamic_validation(schema_request)
