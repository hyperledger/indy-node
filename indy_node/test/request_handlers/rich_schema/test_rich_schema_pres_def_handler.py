import pytest

from indy_common.constants import ENDORSER
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_pres_def_handler import \
    RichSchemaPresDefHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import rich_schema_pres_def_request
from plenum.common.constants import TRUSTEE


@pytest.fixture()
def pres_def_handler(db_manager, write_auth_req_validator):
    return RichSchemaPresDefHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def pres_def_req(pres_def_handler):
    req = rich_schema_pres_def_request()
    add_to_idr(pres_def_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(pres_def_handler.database_manager.idr_cache, req.endorser, ENDORSER)
    return req


def test_schema_dynamic_validation_passes(pres_def_handler, pres_def_req):
    pres_def_handler.dynamic_validation(pres_def_req, 0)
