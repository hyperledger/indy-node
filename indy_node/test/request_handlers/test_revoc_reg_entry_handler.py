import pytest

from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUANCE_BY_DEFAULT, \
    VALUE, ISSUANCE_TYPE, ISSUED, REVOKED, ACCUM
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import RevocRegEntryHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TXN_TIME, STEWARD, TRUSTEE

from plenum.common.exceptions import InvalidClientRequest, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.types import f
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import encode_state_value
from plenum.test.input_validation.conftest import operation
from indy_common.test.auth.conftest import write_auth_req_validator, constraint_serializer, config_state


@pytest.fixture(scope="module")
def revoc_reg_entry_handler(db_manager, write_auth_req_validator):
    return RevocRegEntryHandler(db_manager, write_auth_req_validator,
                                RevocRegDefHandler.get_revocation_strategy)


@pytest.fixture(scope="function")
def revoc_reg_entry_request():
    identifier = randomString()
    return Request(identifier= identifier,
                   reqId=5,
                   operation={'type': REVOC_REG_ENTRY,
                              REVOC_REG_DEF_ID: identifier,
                              VALUE: {ACCUM: 5}},
                   signature="randomString")


def test_revoc_reg_entry_dynamic_validation_without_req_def(revoc_reg_entry_handler,
                                                            revoc_reg_entry_request):
    with pytest.raises(InvalidClientRequest,
                       match="There is no any REVOC_REG_DEF by path"):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)


def test_revoc_reg_entry_dynamic_validation_passes(revoc_reg_entry_handler,
                                                   revoc_reg_entry_request):
    add_to_idr(revoc_reg_entry_handler.database_manager.idr_cache,
               revoc_reg_entry_request.identifier,
               TRUSTEE)

    revoc_reg_entry_handler.state.set(revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
                                      encode_state_value({VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}},
                                                         "seqNo", "txnTime"))
    revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)


def test_revoc_reg_entry_dynamic_validation_fail_in_strategy(revoc_reg_entry_handler,
                                                             revoc_reg_entry_request):
    add_to_idr(revoc_reg_entry_handler.database_manager.idr_cache,
               revoc_reg_entry_request.identifier,
               TRUSTEE)
    revoc_reg_entry_handler.state.set(revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
                                      encode_state_value({VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}},
                                                         "seqNo", "txnTime"))
    revoc_reg_entry_request.operation[VALUE] = {ISSUED: [1],
                                                REVOKED: [1]}
    with pytest.raises(InvalidClientRequest, match="Can not have an index in both "
                                                   "'issued' and 'revoked' lists"):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)


def test_revoc_reg_entry_dynamic_validation_without_permission(revoc_reg_entry_handler,
                                                               revoc_reg_entry_request):
    add_to_idr(revoc_reg_entry_handler.database_manager.idr_cache,
               revoc_reg_entry_request.identifier,
               None)
    revoc_reg_entry_handler.state.set(revoc_reg_entry_request.operation[REVOC_REG_DEF_ID].encode(),
                                      encode_state_value({VALUE: {ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT}},
                                                         "seqNo", "txnTime"))
    revoc_reg_entry_request.operation[VALUE] = {ISSUED: [1],
                                                REVOKED: [1]}
    with pytest.raises(UnauthorizedClientRequest, match="1 TRUSTEE signature is required and needs to be owner OR "
                                                        "1 STEWARD signature is required and needs to be owner OR "
                                                        "1 ENDORSER signature is required and needs to be owner"):
        revoc_reg_entry_handler.dynamic_validation(revoc_reg_entry_request)


def test_failed_update_state(revoc_reg_entry_handler, revoc_reg_entry_request):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(revoc_reg_entry_request)
    append_txn_metadata(txn, seq_no, txn_time)
    with pytest.raises(InvalidClientRequest,
                       match="There is no any REVOC_REG_DEF by path"):
        revoc_reg_entry_handler.update_state(txn, None, revoc_reg_entry_request)


def test_update_state(revoc_reg_entry_handler, revoc_reg_entry_request,
                      revoc_reg_def_handler, revoc_reg_def_request):
    # create revoc_req_def
    seq_no = 1
    txn_time = 1560241030
    revoc_reg_def_request.operation[VALUE] = {}
    revoc_reg_def_request.operation[VALUE][ISSUANCE_TYPE] = ISSUANCE_BY_DEFAULT
    txn = reqToTxn(revoc_reg_def_request)
    append_txn_metadata(txn, seq_no, txn_time)
    path = RevocRegDefHandler.prepare_revoc_def_for_state(txn,
                                                          path_only=True)
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
        RevocRegEntryHandler.prepare_revoc_reg_entry_for_state(txn,
                                                               path_only=True)) == (txn_data, seq_no, txn_time)
    # check state for revoc_reg_entry
    txn_data[VALUE] = {ACCUM: txn_data[VALUE][ACCUM]}
    path, _ = RevocRegEntryHandler.prepare_revoc_reg_entry_accum_for_state(txn)
    assert revoc_reg_entry_handler.get_from_state(path) == (txn_data, seq_no, txn_time)
