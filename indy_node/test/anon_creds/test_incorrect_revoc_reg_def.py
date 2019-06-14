import json

import pytest

from indy_common.constants import CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_SIGNATURE_TYPE, \
    CLAIM_DEF_TAG, VALUE, ISSUANCE_TYPE, REVOKED, PREV_ACCUM, ISSUANCE_BY_DEFAULT
from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.anon_creds.conftest import build_revoc_reg_entry_for_given_revoc_reg_def
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check


def test_incorrect_revoc_reg_def(looper,
                                  txnPoolNodeSet,
                                  sdk_wallet_steward,
                                  sdk_pool_handle,
                                  send_claim_def,
                                  build_revoc_def_by_default):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def[0]
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()

    # test incorrect ISSUANCE_TYPE
    revoc_reg['operation'][VALUE][ISSUANCE_TYPE] = "incorrect_type"
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    with pytest.raises(RequestNackedException, match='unknown value'):
        sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # test correct ISSUANCE_TYPE
    revoc_reg['operation'][VALUE][ISSUANCE_TYPE] = ISSUANCE_BY_DEFAULT
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # send revoc_reg_entry to check that revoc_reg_def ordered correctly
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_req)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry)
    sdk_send_and_check([json.dumps(rev_entry_req)], looper, txnPoolNodeSet, sdk_pool_handle)
