import time

from indy_common.constants import TIMESTAMP
from indy_common.types import SafeRequest
from indy_node.test.anon_creds.helper import build_get_revoc_reg_entry
from plenum.common.constants import TXN_TIME, STATE_PROOF, DATA, DOMAIN_LEDGER_ID
from plenum.common.types import f, OPERATION


def test_validate_get_revoc_reg_entry(looper, sdk_wallet_steward):
    req = build_get_revoc_reg_entry(looper, sdk_wallet_steward)
    SafeRequest(**req)


def test_get_revoc_reg_entry_without_any_rev_entry(send_revoc_reg_def_by_default,
                                                   looper, sdk_wallet_steward,
                                                   txnPoolNodeSet):
    req = build_get_revoc_reg_entry(looper, sdk_wallet_steward)
    req[OPERATION][TIMESTAMP] = int(time.time()) + 2
    result = txnPoolNodeSet[0].read_manager.get_result((SafeRequest(**req)))
    assert result[DATA] is None
    assert result[f.SEQ_NO.nm] is None
    assert result[TXN_TIME] is None
    assert STATE_PROOF in result
    assert result[STATE_PROOF] is not None
