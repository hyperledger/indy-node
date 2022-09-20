import pytest

from common.exceptions import LogicError
from indy_node.server.request_handlers.config_req_handlers.flag_handler import (
    FlagHandler,
)
from indy_node.test.request_handlers.helper import add_to_idr
from indy_common.constants import (
    FLAG,
    FLAG_NAME,
    FLAG_VALUE,
    FLAG_TIME,
    TXN_TYPE,
    NYM,
    ENDORSER,
)
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.util import randomString


@pytest.fixture(scope="module")
def flag_handler(db_manager, write_auth_req_validator):
    return FlagHandler(db_manager, write_auth_req_validator)


@pytest.fixture(scope="function")
def flag_request():
    identifier = randomString()
    return Request(
        identifier=identifier,
        reqId=5,
        operation={TXN_TYPE: FLAG, FLAG_NAME: "REV_REG_ENTRY_SORT", FLAG_VALUE: "True"},
        signature="randomString",
    )


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
