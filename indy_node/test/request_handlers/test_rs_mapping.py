import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_META, RS_DATA
from indy_node.server.request_handlers.domain_req_handlers.rs_mapping_handler import RsMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE, TXN_PAYLOAD
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import append_txn_metadata, reqToTxn


def mapping_exist(rs_mapping_request, rs_mapping_handler):
    txn = reqToTxn(rs_mapping_request)
    path, state_value = rs_mapping_handler.prepare_state(txn)
    rs_mapping_handler.state.set(path, state_value)


def test_rs_mapping_dynamic_validation_failed_existing_mapping(rs_mapping_request, rs_mapping_handler):
    mapping_exist(rs_mapping_request, rs_mapping_handler)
    with pytest.raises(UnauthorizedClientRequest, match=str(AuthConstraintForbidden())):
        rs_mapping_handler.dynamic_validation(rs_mapping_request, 0)


def test_rs_mapping_dynamic_validation_failed_not_authorised(rs_mapping_request, rs_mapping_handler):
    add_to_idr(rs_mapping_handler.database_manager.idr_cache, rs_mapping_request.identifier, None)
    with pytest.raises(UnauthorizedClientRequest):
        rs_mapping_handler.dynamic_validation(rs_mapping_request, 0)


def test_rs_mapping_dynamic_validation_passes(rs_mapping_request, rs_mapping_handler):
    add_to_idr(rs_mapping_handler.database_manager.idr_cache, rs_mapping_request.identifier, TRUSTEE)
    rs_mapping_handler.dynamic_validation(rs_mapping_request, 0)


def test_update_state(rs_mapping_request, rs_mapping_handler):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(rs_mapping_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path, value_bytes = RsMappingHandler.prepare_state(txn)
    payload = txn[TXN_PAYLOAD][RS_DATA]
    meta, data = payload[RS_META], payload[RS_DATA]
    value = {
        RS_META: meta,
        RS_DATA: data
    }
    rs_mapping_handler.update_state(txn, None, rs_mapping_request)
    assert rs_mapping_handler.get_from_state(path) == (value, seq_no, txn_time)