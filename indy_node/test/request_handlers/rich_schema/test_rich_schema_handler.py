import pytest

from indy_common.constants import ENDORSER
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_request
from plenum.common.constants import TRUSTEE


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req(rich_schema_handler):
    req = rich_schema_request()
    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.endorser, ENDORSER)
    return req


def test_schema_dynamic_validation_passes(rich_schema_handler, rich_schema_req):
    rich_schema_handler.dynamic_validation(rich_schema_req, 0)
