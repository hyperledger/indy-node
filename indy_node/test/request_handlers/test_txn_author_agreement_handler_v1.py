import pytest as pytest

from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_handler_v1 import \
    TxnAuthorAgreementHandlerV1
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT_VERSION, DOMAIN_LEDGER_ID
from plenum.common.txn_util import reqToTxn, get_payload_data, append_txn_metadata
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.static_taa_helper import StaticTAAHelper
from plenum.test.testing_utils import FakeSomething
from state.state import State


@pytest.fixture(scope="function")
def txn_author_agreement_handler(tconf, domain_state, write_auth_req_validator):
    data_manager = DatabaseManager()
    handler = TxnAuthorAgreementHandlerV1(data_manager, write_auth_req_validator)
    state = State()
    state.txn_list = {}
    state.get = lambda key, isCommitted=False: state.txn_list.get(key, None)
    state.set = lambda key, value, isCommitted=False: state.txn_list.update({key: value})
    data_manager.register_new_database(handler.ledger_id,
                                       FakeSomething(),
                                       state)
    data_manager.register_new_database(DOMAIN_LEDGER_ID,
                                       FakeSomething(),
                                       domain_state)
    return handler


def test_update_state(txn_author_agreement_handler, taa_request):
    seq_no = 1
    txn_time = 1560241033
    txn_id = "id"
    txn = reqToTxn(taa_request)
    payload = get_payload_data(txn)
    text = payload[TXN_AUTHOR_AGREEMENT_TEXT]
    version = payload[TXN_AUTHOR_AGREEMENT_VERSION]
    digest = StaticTAAHelper.taa_digest(text, version)
    append_txn_metadata(txn, seq_no, txn_time, txn_id)

    state_value = {TXN_AUTHOR_AGREEMENT_TEXT: text,
                   TXN_AUTHOR_AGREEMENT_VERSION: version}

    txn_author_agreement_handler.update_state(txn, None, taa_request)

    assert txn_author_agreement_handler.get_from_state(
        StaticTAAHelper.state_path_taa_digest(digest)) == (state_value, seq_no, txn_time)
    assert txn_author_agreement_handler.state.get(
        StaticTAAHelper.state_path_taa_latest()) == digest
    assert txn_author_agreement_handler.state.get(
        StaticTAAHelper.state_path_taa_version(version)) == digest
