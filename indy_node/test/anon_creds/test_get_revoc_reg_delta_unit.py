import pytest

from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_delta_handler import GetRevocRegDeltaHandler
from indy_node.test.anon_creds.helper import build_get_revoc_reg_delta
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_txn_time
from plenum.common.types import f
from indy_common.types import Request
from plenum.common.constants import TXN_TIME, DOMAIN_LEDGER_ID
from indy_common.state import domain
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.common.util import randomString
from indy_node.test.anon_creds.conftest import build_revoc_reg_entry_for_given_revoc_reg_def
from indy_common.constants import REVOC_REG_DEF_ID, REVOC_REG_DEF, ISSUANCE_BY_DEFAULT, \
    CRED_DEF_ID, VALUE, TAG, ID, TXN_TYPE, REVOC_TYPE, ISSUANCE_TYPE, MAX_CRED_NUM, \
    TAILS_HASH, TAILS_LOCATION, PUBLIC_KEYS, FROM


FIRST_ID_TS = 1000
SECOND_TS_ID = 2000


@pytest.fixture(scope="module")
def add_another_reg_id(looper,
                       sdk_wallet_steward,
                       create_node_and_not_start):
    node = create_node_and_not_start
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: randomString(50),
        VALUE:{
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    looper.runFor(2)
    txn = append_txn_metadata(reqToTxn(Request(**req)),
                              txn_time=FIRST_ID_TS,
                              seq_no=node.domainLedger.seqNo + 1)
    node.write_manager.update_state(txn)
    return req


@pytest.fixture(scope="function")
def reg_entry_with_other_reg_id(looper,
                                sdk_wallet_steward,
                                add_another_reg_id,
                                create_node_and_not_start):
    node = create_node_and_not_start
    revoc_def_txn = add_another_reg_id
    data = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_txn)
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    looper.runFor(2)
    txn = append_txn_metadata(reqToTxn(Request(**req)),
                              txn_time=FIRST_ID_TS,
                              seq_no=node.domainLedger.seqNo + 1)
    node.write_manager.update_state(txn)
    node.db_manager.ts_store.set(get_txn_time(txn), node.db_manager.get_state(DOMAIN_LEDGER_ID).headHash)
    return txn


def test_get_delta_with_other_reg_def_in_state(looper,
                                               create_node_and_not_start,
                                               reg_entry_with_other_reg_id,
                                               build_txn_for_revoc_def_entry_by_default,
                                               sdk_wallet_steward):
    entry_second_id = build_txn_for_revoc_def_entry_by_default
    delta_req = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    node = create_node_and_not_start
    # need for different txnTime
    looper.runFor(2)
    txn = append_txn_metadata(reqToTxn(entry_second_id),
                              txn_time=SECOND_TS_ID,
                              seq_no=node.domainLedger.seqNo + 1)
    node.write_manager.update_state(txn)
    node.db_manager.ts_store.set(get_txn_time(txn), node.getState(DOMAIN_LEDGER_ID).headHash)

    # timestamp beetween FIRST_ID_TS and SECOND_ID_TS
    delta_req['operation'][FROM] = FIRST_ID_TS + 10
    path_to_reg_entry = domain.make_state_path_for_revoc_reg_entry(
        revoc_reg_def_id=entry_second_id['operation'][REVOC_REG_DEF_ID])

    req_handler = None
    for h in node.read_manager.request_handlers.values():
        if isinstance(h, GetRevocRegDeltaHandler):
            req_handler = h

    reg_entry = req_handler._get_reg_entry_by_timestamp(
        delta_req['operation'][FROM],
        path_to_reg_entry)
    # we found root_hash in txRevoc storage but there is not corresponded reg_entry by path
    assert reg_entry.root_hash is not None
    assert reg_entry.value is None

    path_to_reg_entry_accum = domain.make_state_path_for_revoc_reg_entry(
        revoc_reg_def_id=entry_second_id['operation'][REVOC_REG_DEF_ID])
    reg_entry_accum = req_handler._get_reg_entry_accum_by_timestamp(
        delta_req['operation'][FROM],
        path_to_reg_entry_accum)
    assert reg_entry_accum.root_hash is not None
    assert reg_entry_accum.value is None


