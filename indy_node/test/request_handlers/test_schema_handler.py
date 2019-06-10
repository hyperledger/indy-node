import pytest

from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.constants import SCHEMA
from indy_common.req_utils import get_write_schema_name, get_write_schema_version
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr, get_exception
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest
from plenum.common.txn_util import get_request_data
from plenum.server.request_handlers.utils import encode_state_value
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def schema_handler(db_manager):
    f_validator = FakeSomething()
    f_validator.validate = lambda request, action_list: True
    return SchemaHandler(db_manager, f_validator)


def make_schema_exist(schema_request, schema_handler):
    identifier, req_id, operation = get_request_data(schema_request)
    schema_name = get_write_schema_name(schema_request)
    schema_version = get_write_schema_version(schema_request)
    path = SchemaHandler.make_state_path_for_schema(identifier, schema_name, schema_version)
    schema_handler.state.set(path, encode_state_value("value", "seqNo", "txnTime"))


def test_schema_dynamic_validation_failed_existing_schema(schema_request, schema_handler):
    make_schema_exist(schema_request, schema_handler)

    def validate(request, action_list):
        if action_list[0].get_action_id() == AuthActionEdit(txn_type=SCHEMA,
                                                            field='*',
                                                            old_value='*',
                                                            new_value='*').get_action_id():
            raise UnauthorizedClientRequest("identifier", "reqId")

    schema_handler.write_req_validator.validate = validate

    with pytest.raises(UnauthorizedClientRequest):
        schema_handler.dynamic_validation(schema_request)


def test_schema_dynamic_validation_failed_not_authorised(schema_request, schema_handler):
    schema_handler.write_req_validator.validate = get_exception(True)
    add_to_idr(schema_handler.database_manager.idr_cache, schema_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        schema_handler.dynamic_validation(schema_request)


def test_schema_dynamic_validation_passes(schema_request, schema_handler):
    schema_handler.write_req_validator.validate = get_exception(False)
    add_to_idr(schema_handler.database_manager.idr_cache, schema_request.identifier, TRUSTEE)
    schema_handler.dynamic_validation(schema_request)
