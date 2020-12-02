import pytest

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import SCHEMA_ATTR_NAMES
from indy_common.req_utils import get_write_schema_name, get_write_schema_version, get_txn_schema_attr_names
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import get_request_data, reqToTxn, append_txn_metadata
from plenum.server.request_handlers.utils import encode_state_value


def make_schema_exist(schema_request, schema_handler):
    identifier, req_id, operation = get_request_data(schema_request)
    schema_name = get_write_schema_name(schema_request)
    schema_version = get_write_schema_version(schema_request)
    path = SchemaHandler.make_state_path_for_schema(identifier, schema_name, schema_version)
    schema_handler.state.set(path, encode_state_value("value", "seqNo", "txnTime"))


def test_schema_dynamic_validation_failed_existing_schema(schema_request, schema_handler):
    make_schema_exist(schema_request, schema_handler)
    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        schema_handler.dynamic_validation(schema_request, 0)


def test_schema_dynamic_validation_failed_not_authorised(schema_request, schema_handler):
    add_to_idr(schema_handler.database_manager.idr_cache, schema_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        schema_handler.dynamic_validation(schema_request, 0)


def test_schema_dynamic_validation_passes(schema_request, schema_handler):
    add_to_idr(schema_handler.database_manager.idr_cache, schema_request.identifier, TRUSTEE)
    schema_handler.dynamic_validation(schema_request, 0)


def test_update_state(schema_request, schema_handler):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(schema_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path, value_bytes = SchemaHandler.prepare_schema_for_state(txn)
    value = {
        SCHEMA_ATTR_NAMES: get_txn_schema_attr_names(txn)
    }

    schema_handler.update_state(txn, None, schema_request)
    assert schema_handler.get_from_state(path) == (value, seq_no, txn_time)
