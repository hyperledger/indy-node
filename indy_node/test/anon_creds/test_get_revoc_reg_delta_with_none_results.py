import copy
import json

from indy_common.constants import REVOC_REG_DEF_ID, TO, CRED_DEF_ID, REVOC_TYPE, TAG, VALUE, STATE_PROOF_FROM, \
    ACCUM_FROM
from indy_common.state import domain
from indy_node.test.anon_creds.helper import build_get_revoc_reg_delta
from plenum.common.constants import DATA, STATE_PROOF
from plenum.common.types import f, OPERATION
from plenum.common.util import get_utc_epoch
from plenum.test.helper import sdk_send_and_check


def test_send_reg_def_and_get_delta_then(
        looper,
        txnPoolNodeSet,
        sdk_pool_handle,
        send_revoc_reg_def_by_default,
        sdk_wallet_steward):
    rev_def_req, _ = send_revoc_reg_def_by_default
    get_revoc_reg_delta = build_get_revoc_reg_delta(looper, sdk_wallet_steward)
    get_revoc_reg_delta['operation'][REVOC_REG_DEF_ID] = domain.make_state_path_for_revoc_def(authors_did=rev_def_req[f.IDENTIFIER.nm],
                                                                                              cred_def_id=rev_def_req[OPERATION][CRED_DEF_ID],
                                                                                              revoc_def_type=rev_def_req[OPERATION][REVOC_TYPE],
                                                                                              revoc_def_tag=rev_def_req[OPERATION][TAG]).decode()
    get_revoc_reg_delta['operation'][TO] = get_utc_epoch()
    sdk_reply = sdk_send_and_check([json.dumps(get_revoc_reg_delta)], looper, txnPoolNodeSet, sdk_pool_handle)
    reply = sdk_reply[0][1]
    assert DATA in reply['result']
    assert reply['result'][DATA][STATE_PROOF_FROM] is None
    assert reply['result'][DATA][VALUE][ACCUM_FROM] is None
    assert STATE_PROOF in reply['result']
    assert reply['result'][STATE_PROOF] is not None
