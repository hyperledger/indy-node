import pytest

from common.exceptions import LogicError
from indy_node.server.request_handlers.config_req_handlers.flag_handler import (
    FlagHandler,
)
from indy_node.test.request_handlers.conftest import flag_request, flag_handler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_common.constants import (
    FLAG,
    FLAG_NAME,
    FLAG_VALUE,
    TXN_TYPE,
    NYM,
    ENDORSER,
)
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.util import randomString


def test_config_flag_static_validation_wrong_type(
    flag_handler: FlagHandler, flag_request: Request
):
    with pytest.raises(LogicError):
        flag_request.operation[TXN_TYPE] = NYM
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_no_key(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    flag_request.operation[FLAG_NAME] = None
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    with pytest.raises(InvalidClientRequest, match="Flag name is required"):
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_empty_key(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    flag_request.operation[FLAG_NAME] = ""
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    with pytest.raises(InvalidClientRequest, match="Flag name is required"):
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_wrong_name_type(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    flag_request.operation[FLAG_NAME] = 123
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    with pytest.raises(InvalidClientRequest, match="Flag name must be of type string"):
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_wrong_value_type(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    flag_request.operation[FLAG_VALUE] = True
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    with pytest.raises(InvalidClientRequest, match="Flag value must be of type string or None"):
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_pass(
    flag_handler: FlagHandler, flag_request: Request
):
    flag_handler.static_validation(flag_request)


def test_config_flag_dynamic_validation_authorize_not_trustee(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache, flag_request.identifier, ENDORSER
    )
    with pytest.raises(
        UnauthorizedClientRequest, match=".*'Not enough TRUSTEE signatures'"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)

    add_to_idr(
        flag_handler.database_manager.idr_cache, flag_request.identifier, STEWARD
    )
    with pytest.raises(
        UnauthorizedClientRequest, match=".*'Not enough TRUSTEE signatures'"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_dynamic_validation_authorize_no_nym(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    with pytest.raises(
        UnauthorizedClientRequest, match=".* is not found in the Ledger"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_dynamic_validation_authorize_no_permission(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(flag_handler.database_manager.idr_cache, flag_request.identifier, None)
    with pytest.raises(
        UnauthorizedClientRequest, match=".*'Not enough TRUSTEE signatures'"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_dynamic_validation_authorize_passes(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_update_state_no_value(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    flag_request.operation[FLAG_VALUE] = None
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 2
    txn_time = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    path = FlagHandler.make_state_path_for_flag(key)
    state = flag_handler.get_from_state(path)
    assert(state)
    state_value = FlagHandler.get_state_value(state)
    assert(state_value is None)
    state_time = FlagHandler.get_state_timestamp(state)
    assert(state_time == txn_time)


def test_config_flag_update_state_empty_value(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    flag_request.operation[FLAG_VALUE] = ""
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 2
    txn_time = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    path = FlagHandler.make_state_path_for_flag(key)
    state = flag_handler.get_from_state(path)
    assert(state)
    state_value = FlagHandler.get_state_value(state)
    assert(state_value == "")
    state_time = FlagHandler.get_state_timestamp(state)
    assert(state_time == txn_time)


def test_config_flag_update_state_correct_value(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    val = "True"
    flag_request.operation[FLAG_VALUE] = val
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 2
    txn_time = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    path = FlagHandler.make_state_path_for_flag(key)
    state = flag_handler.get_from_state(path)
    assert(state)
    state_value = FlagHandler.get_state_value(state)
    assert(state_value == val)
    state_time = FlagHandler.get_state_timestamp(state)
    assert(state_time == txn_time)


def test_config_flag_update_state_edit(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    val_old = "old_value"
    flag_request.operation[FLAG_VALUE] = val_old
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 2
    txn_time_old = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time_old)
    flag_handler.update_state(txn, None, flag_request)
    old_head_hash = flag_handler.state.headHash
    assert(old_head_hash)
    (value, timestamp) = flag_handler.get_state(key)
    assert(value == val_old)
    assert(timestamp == txn_time_old)

    val_new = "new_value"
    flag_request.operation[FLAG_VALUE] = val_new
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 3
    txn_time = 1560251034
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)

    (value, timestamp) = flag_handler.get_state(key)
    assert(value == val_new)
    assert(timestamp == txn_time)

    # check old state
    path = FlagHandler.make_state_path_for_flag(key)
    state_encoded = flag_handler.state.get_for_root_hash(old_head_hash, path)
    state_raw = flag_handler._decode_state_value(state_encoded)
    value = FlagHandler.get_state_value(state_raw)
    timestamp = FlagHandler.get_state_timestamp(state_raw)
    assert(value == val_old)
    assert(timestamp == txn_time_old)


def test_config_flag_get_state_empty_key(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    seq_no = 2
    txn_time = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)

    (value, timestamp) = flag_handler.get_state("")
    assert(value is None)
    assert(timestamp is None)


def test_config_flag_get_state_valid(
    flag_handler: FlagHandler,
    flag_request: Request,
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    val = "Test12345"
    flag_request.operation[FLAG_VALUE] = val
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 2
    txn_time = 1560241033
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)

    (value, timestamp) = flag_handler.get_state(key)
    assert(value == val)
    assert(timestamp == txn_time)
