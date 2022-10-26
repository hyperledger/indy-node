import pytest

from common.exceptions import LogicError
from indy_node.server.request_handlers.config_req_handlers.flag_handler import (
    FlagRequestHandler,
)
from indy_node.server.request_handlers.read_req_handlers.get_flag_handler import GetFlagRequestHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_common.constants import (
    CONFIG_LEDGER_ID,
    FLAG_NAME,
    FLAG_VALUE,
    GET_FLAG,
    TXN_TYPE,
    NYM,
    ENDORSER,
    VERSION_ID,
    VERSION_TIME,
)
from plenum.common.constants import TRUSTEE, STEWARD, DATA, STATE_PROOF, TXN_TIME
from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.types import f

@pytest.fixture(scope="function")
def get_flag_request(creator):
    return Request(identifier=creator,
                   reqId=5,
                   operation={TXN_TYPE: GET_FLAG})


def test_config_flag_static_validation_wrong_type(
    flag_handler: FlagRequestHandler, flag_request: Request
):
    with pytest.raises(LogicError):
        flag_request.operation[TXN_TYPE] = NYM
        flag_handler.static_validation(flag_request)


def test_config_flag_static_validation_no_key(
    flag_handler: FlagRequestHandler,
    flag_request: Request
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
    flag_handler: FlagRequestHandler,
    flag_request: Request
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
    flag_handler: FlagRequestHandler,
    flag_request: Request
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
    flag_handler: FlagRequestHandler,
    flag_request: Request
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
    flag_handler: FlagRequestHandler, flag_request: Request
):
    flag_handler.static_validation(flag_request)


def test_config_flag_dynamic_validation_authorize_not_trustee(
    flag_handler: FlagRequestHandler,
    flag_request: Request
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
    flag_handler: FlagRequestHandler,
    flag_request: Request
):
    with pytest.raises(
        UnauthorizedClientRequest, match=".* is not found in the Ledger"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_dynamic_validation_authorize_no_permission(
    flag_handler: FlagRequestHandler,
    flag_request: Request
):
    add_to_idr(flag_handler.database_manager.idr_cache, flag_request.identifier, None)
    with pytest.raises(
        UnauthorizedClientRequest, match=".*'Not enough TRUSTEE signatures'"
    ):
        flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_dynamic_validation_authorize_passes(
    flag_handler: FlagRequestHandler,
    flag_request: Request
):
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )
    flag_handler.additional_dynamic_validation(flag_request, 0)


def test_config_flag_update_state_no_value(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler
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
    flag_handler.state.commit()

    # lookup
    state = get_flag_request_handler.lookup_key(key)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value is None)


def test_config_flag_update_state_empty_value(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler
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
    flag_handler.state.commit()

    state = get_flag_request_handler.lookup_key(key)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value == "")


def test_config_flag_update_state_correct_value(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler
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
    flag_handler.state.commit()
    state = get_flag_request_handler.lookup_key(key)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value == val)


def test_config_flag_update_state_edit(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler
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
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time_old, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)

    val_new = "new_value"
    flag_request.operation[FLAG_VALUE] = val_new
    key = flag_request.operation.get(FLAG_NAME)
    seq_no = 3
    txn_time = 1560251034
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)

    # check current state
    state = get_flag_request_handler.lookup_key(key)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value == val_new)

    # check old state
    state = get_flag_request_handler.lookup_key(key, timestamp=txn_time_old)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value == val_old)

    # check for None state before
    state = get_flag_request_handler.lookup_key(key, timestamp=(txn_time_old - 1))
    assert(state is None)


def test_config_flag_get_result_exclusive(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler,
    get_flag_request: Request
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
    flag_handler.state.commit()

    state = get_flag_request_handler.lookup_key(key)
    assert(state)
    state_value = FlagRequestHandler.get_state_value(state)
    assert(state_value == val)

    get_flag_request.operation[FLAG_NAME] = key
    get_flag_request.operation[VERSION_TIME] = txn_time
    get_flag_request.operation[VERSION_ID] = seq_no

    with pytest.raises(
        InvalidClientRequest, match=".*seqNo and timestamp are mutually exclusive; only one should be specified"
    ):
        get_flag_request_handler.get_result(get_flag_request)


def test_config_flag_get_state_empty_key(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler
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
    flag_handler.state.commit()

    value = get_flag_request_handler.lookup_key("")
    assert(value is None)


def test_config_flag_get_result_valid(
    flag_handler: FlagRequestHandler,
    flag_request: Request,
    get_flag_request_handler: GetFlagRequestHandler,
    get_flag_request: Request,
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
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)

    get_flag_request.operation[FLAG_NAME] = key
    result = get_flag_request_handler.get_result(get_flag_request)
    assert(result.get(TXN_TYPE) == GET_FLAG)
    assert(result.get(TXN_TIME) == txn_time)
    assert(result.get(f.SEQ_NO.nm) == seq_no)
    state_value = FlagRequestHandler.get_state_value(result.get(DATA))
    assert(state_value == val)
    assert(result.get(STATE_PROOF) is None)
