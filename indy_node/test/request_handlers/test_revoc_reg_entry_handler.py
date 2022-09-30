import pytest

from indy_common.constants import (
    FLAG_NAME,
    FLAG_NAME_COMPAT_ORDERING,
    FLAG_VALUE,
    REVOC_REG_ENTRY,
    REVOC_REG_DEF_ID,
    ISSUANCE_BY_DEFAULT,
    VALUE,
    ISSUANCE_TYPE,
    ISSUED,
    REVOKED,
    ACCUM,
    REVOC_REG_DEF,
    CRED_DEF_ID,
    REVOC_TYPE,
    TAG,
    CONFIG_LEDGER_ID
)
from indy_common.config_util import getConfig
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import (
    RevocRegDefHandler,
)
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import (
    RevocRegEntryHandler,
)
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TXN_TIME, TRUSTEE

from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.types import f
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import encode_state_value
from plenum.server.node import Node

@pytest.fixture(scope="function")
def revoc_reg_entry_handler(db_manager_ts, write_auth_req_validator):
    node = Node.__new__(Node)
    return RevocRegEntryHandler(
        db_manager_ts, write_auth_req_validator, RevocRegDefHandler.get_revocation_strategy, node
    )


@pytest.fixture(scope="function")
def revoc_reg_entry_request():
    identifier = randomString()
    return Request(
        identifier=identifier,
        reqId=5,
        operation={
            "type": REVOC_REG_ENTRY,
            REVOC_REG_DEF_ID: identifier,
            VALUE: {ACCUM: 5},
        },
        signature="randomString",
    )


def test_revoc_reg_entry_dynamic_validation_without_req_def(
    revoc_reg_entry_handler, revoc_reg_entry_request
):
    with pytest.raises(
        InvalidClientRequest, match="There is no any REVOC_REG_DEF by path"
    ):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request, 0)


def test_revoc_reg_entry_dynamic_validation_passes(
    revoc_reg_entry_handler, revoc_reg_entry_request
):
    add_to_idr(
        revoc_reg_entry_handler.database_manager.idr_cache,
        revoc_reg_entry_request.identifier,
        TRUSTEE,
    )

    revoc_reg_entry_handler.state.set(
        revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
        encode_state_value(
            {VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}}, "seqNo", "txnTime"
        ),
    )
    revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request, 0)


def test_revoc_reg_entry_dynamic_validation_fail_in_strategy(
    revoc_reg_entry_handler, revoc_reg_entry_request
):
    add_to_idr(
        revoc_reg_entry_handler.database_manager.idr_cache,
        revoc_reg_entry_request.identifier,
        TRUSTEE,
    )
    revoc_reg_entry_handler.state.set(
        revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
        encode_state_value(
            {VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}}, "seqNo", "txnTime"
        ),
    )
    revoc_reg_entry_request.operation[VALUE] = {ISSUED: [1], REVOKED: [1]}
    with pytest.raises(
        InvalidClientRequest,
        match="Can not have an index in both " "'issued' and 'revoked' lists",
    ):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request, 0)


def test_revoc_reg_entry_dynamic_validation_without_permission(
    revoc_reg_entry_handler, revoc_reg_entry_request
):
    add_to_idr(
        revoc_reg_entry_handler.database_manager.idr_cache,
        revoc_reg_entry_request.identifier,
        None,
    )
    revoc_reg_entry_handler.state.set(
        revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
        encode_state_value(
            {VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}}, "seqNo", "txnTime"
        ),
    )
    revoc_reg_entry_request.operation[VALUE] = {ISSUED: [1], REVOKED: [1]}
    with pytest.raises(
        UnauthorizedClientRequest,
        match="1 TRUSTEE signature is required and needs to be owner OR "
        "1 STEWARD signature is required and needs to be owner OR "
        "1 ENDORSER signature is required and needs to be owner",
    ):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request, 0)


def test_failed_update_state(revoc_reg_entry_handler, revoc_reg_entry_request):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(revoc_reg_entry_request)
    append_txn_metadata(txn, seq_no, txn_time)
    with pytest.raises(
        InvalidClientRequest, match="There is no any REVOC_REG_DEF by path"
    ):
        revoc_reg_entry_handler.update_state(txn, None, revoc_reg_entry_request)


def test_update_state(
    revoc_reg_entry_handler,
    revoc_reg_entry_request,
    revoc_reg_def_handler,
    revoc_reg_def_request,
):
    # create revoc_req_def
    seq_no = 1
    txn_time = 1560241030
    revoc_reg_def_request.operation[VALUE] = {}
    revoc_reg_def_request.operation[VALUE][ISSUANCE_TYPE] = ISSUANCE_BY_DEFAULT
    txn = reqToTxn(revoc_reg_def_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path = RevocRegDefHandler.prepare_revoc_def_for_state(txn, path_only=True)
    revoc_reg_def_handler.update_state(txn, None, revoc_reg_def_request)

    # create revoc_req_entry
    seq_no = 2
    txn_time = 1560241033
    revoc_reg_entry_request.operation[REVOC_REG_DEF_ID] = path.decode()
    txn = reqToTxn(revoc_reg_entry_request)
    append_txn_metadata(txn, seq_no, txn_time)
    revoc_reg_entry_handler.update_state(txn, None, revoc_reg_entry_request)

    # check state for revoc_reg_entry
    txn_data = get_payload_data(txn)
    txn_data[f.SEQ_NO.nm] = seq_no
    txn_data[TXN_TIME] = txn_time
    assert revoc_reg_entry_handler.get_from_state(
        RevocRegEntryHandler.prepare_revoc_reg_entry_for_state(txn, path_only=True)
    ) == (txn_data, seq_no, txn_time)
    # check state for revoc_reg_entry
    txn_data[VALUE] = {ACCUM: txn_data[VALUE][ACCUM]}
    path, _ = RevocRegEntryHandler.prepare_revoc_reg_entry_accum_for_state(txn)
    assert revoc_reg_entry_handler.get_from_state(path) == (txn_data, seq_no, txn_time)


def test_legacy_switch_by_default_new(
    revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler
):
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler
    )
    assert state[VALUE][REVOKED] == [5, 6, 12, 13]


def test_legacy_switch_old(
    revoc_reg_entry_request,
    revoc_reg_def_handler,
    revoc_reg_entry_handler
):
    revoc_reg_entry_handler.legacy_sort_config = True

    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler
    )
    assert state[VALUE][REVOKED] == [12, 13, 5, 6]


def _test_ordering(
    revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=1, txn_time=1560241030
):
    # create revoc_req_def
    # Force a new rev reg def for these tests
    revoc_reg_def_request = Request(
        identifier=randomString(),
        reqId=5,
        signature="sig",
        operation={
            "type": REVOC_REG_DEF,
            CRED_DEF_ID: "credDefId",
            REVOC_TYPE: randomString(),
            TAG: randomString(),
        },
    )

    revoc_reg_def_request.operation[VALUE] = {}
    revoc_reg_def_request.operation[VALUE][ISSUANCE_TYPE] = ISSUANCE_BY_DEFAULT
    txn = reqToTxn(revoc_reg_def_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path = RevocRegDefHandler.prepare_revoc_def_for_state(txn, path_only=True)
    revoc_reg_def_handler.update_state(txn, None, revoc_reg_def_request)

    # create first revoc_req_entry
    seq_no += 1
    txn_time += 50
    revoc_reg_entry_request.operation[REVOC_REG_DEF_ID] = path.decode()
    revoc_reg_entry_request.operation[VALUE][ISSUED] = []
    revoc_reg_entry_request.operation[VALUE][REVOKED] = [4, 5, 6, 12]
    txn = reqToTxn(revoc_reg_entry_request)
    append_txn_metadata(txn, seq_no, txn_time)
    revoc_reg_entry_handler.update_state(txn, None, revoc_reg_entry_request)

    # create second revoc_req_entry
    seq_no += 1
    txn_time += 123
    revoc_reg_entry_request.operation[REVOC_REG_DEF_ID] = path.decode()
    revoc_reg_entry_request.operation[VALUE][ISSUED] = [4]
    revoc_reg_entry_request.operation[VALUE][REVOKED] = [13]
    txn = reqToTxn(revoc_reg_entry_request)
    append_txn_metadata(txn, seq_no, txn_time)
    revoc_reg_entry_handler.update_state(txn, None, revoc_reg_entry_request)
    state = revoc_reg_entry_handler.get_from_state(
        RevocRegEntryHandler.prepare_revoc_reg_entry_for_state(txn, path_only=True)
    )
    return state[0]


def test_ordering_switch_via_transaction(
    flag_handler,
    flag_request,
    get_flag_request_handler,
    revoc_reg_def_handler,
    revoc_reg_entry_handler,
    revoc_reg_entry_request
):
    # enable legacy sorting
    revoc_reg_entry_handler.legacy_sort_config = True

    # First run to make sure legacy sorting works
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=1
    )
    assert state[VALUE][REVOKED] == [12, 13, 5, 6]

    # config flag transaction
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    seq_no = 4
    txn_time = 1560241033
    flag_request.operation[FLAG_NAME] = FLAG_NAME_COMPAT_ORDERING
    flag_request.operation[FLAG_VALUE] = "False"
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)

    # Second run to test the switch to proper sorting via config transaction
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=5
    )
    assert state[VALUE][REVOKED] == [5, 6, 12, 13]


def test_ordering_switch_via_transaction_catchup(
    flag_handler,
    get_flag_request_handler,
    flag_request,
    revoc_reg_def_handler,
    revoc_reg_entry_handler,
    revoc_reg_entry_request
):

    # enable legacy sorting locally
    revoc_reg_entry_handler.legacy_sort_config = True

    # config flag transaction
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    seq_no = 1
    txn_time = 156025000
    flag_request.operation[FLAG_NAME] = FLAG_NAME_COMPAT_ORDERING
    flag_request.operation[FLAG_VALUE] = "False"
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)

    # First run to make sure legacy sorting works
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=2, txn_time=156021000
    )
    assert state[VALUE][REVOKED] == [12, 13, 5, 6]

    # Second run to test the switch to proper sorting via config transaction
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=5, txn_time=156029000
    )
    assert state[VALUE][REVOKED] == [5, 6, 12, 13]


def test_ordering_switch_via_transaction_catchup_locally(
    flag_handler,
    flag_request,
    get_flag_request_handler,
    revoc_reg_def_handler,
    revoc_reg_entry_handler,
    revoc_reg_entry_request
):

    # disable legacy sorting locally
    revoc_reg_entry_handler.legacy_sort_config = False

    # config flag transaction
    add_to_idr(
        flag_handler.database_manager.idr_cache,
        flag_request.identifier,
        TRUSTEE,
    )

    seq_no = 1
    txn_time = 156025000
    flag_request.operation[FLAG_NAME] = FLAG_NAME_COMPAT_ORDERING
    flag_request.operation[FLAG_VALUE] = "False"
    txn = reqToTxn(flag_request)
    append_txn_metadata(txn, seq_no, txn_time)
    flag_handler.update_state(txn, None, flag_request)
    flag_handler.state.commit()
    get_flag_request_handler.timestamp_store.set(txn_time, flag_handler.state.headHash, ledger_id=CONFIG_LEDGER_ID)


    # First run to make sure we use new sorting before the transaction time because of local sort setting
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=2, txn_time=156021000
    )
    assert state[VALUE][REVOKED] == [5, 6, 12, 13]

    # Second run to test the switch to proper sorting via config transaction
    state = _test_ordering(
        revoc_reg_entry_handler, revoc_reg_entry_request, revoc_reg_def_handler, seq_no=5, txn_time=156029000
    )
    assert state[VALUE][REVOKED] == [5, 6, 12, 13]
