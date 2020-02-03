import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_META, RS_DATA
from indy_node.server.request_handlers.domain_req_handlers.rs_schema_handler import RsSchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE, TXN_PAYLOAD
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import append_txn_metadata, reqToTxn


def make_rs_schema_exist(rs_schema_request, rs_schema_handler):
    txn = reqToTxn(rs_schema_request)
    path, encoded_state_value = rs_schema_handler.prepare_state(txn)
    rs_schema_handler.state.set(path, encoded_state_value)


def test_rs_schema_dynamic_validation_failed_existing_schema(rs_schema_request, rs_schema_handler):
    make_rs_schema_exist(rs_schema_request, rs_schema_handler)
    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        rs_schema_handler.dynamic_validation(rs_schema_request, 0)


def test_rs_schema_dynamic_validation_failed_not_authorised(rs_schema_request, rs_schema_handler):
    add_to_idr(rs_schema_handler.database_manager.idr_cache, rs_schema_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        rs_schema_handler.dynamic_validation(rs_schema_request, 0)


def test_rs_schema_dynamic_validation_passes(rs_schema_request, rs_schema_handler):
    add_to_idr(rs_schema_handler.database_manager.idr_cache, rs_schema_request.identifier, TRUSTEE)
    rs_schema_handler.dynamic_validation(rs_schema_request, 0)


def test_adam_rs_schema_nightmare(rs_schema_broken_request, rs_schema_handler):
    add_to_idr(rs_schema_handler.database_manager.idr_cache, rs_schema_broken_request.identifier, TRUSTEE)
    rs_schema_handler.dynamic_validation(rs_schema_broken_request, 0)


def test_update_state(rs_schema_request, rs_schema_handler):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(rs_schema_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path, value_bytes = RsSchemaHandler.prepare_state(txn)
    payload = txn[TXN_PAYLOAD][RS_DATA]
    meta, data = payload[RS_META], payload[RS_DATA]
    value = {
        RS_META: meta,
        RS_DATA: data
    }
    rs_schema_handler.update_state(txn, None, rs_schema_request)
    assert rs_schema_handler.get_from_state(path) == (value, seq_no, txn_time)
