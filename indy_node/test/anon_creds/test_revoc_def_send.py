import json

from indy_common.constants import CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG
from indy_common.state.domain import make_state_path_for_claim_def
from plenum.test.helper import sdk_send_and_check
from plenum.test.helper import sdk_sign_request_from_dict


def test_send_revoc_reg_def(looper,
                            txnPoolNodeSet,
                            sdk_wallet_steward,
                            sdk_pool_handle,
                            build_revoc_def_by_default,
                            send_claim_def):
    txns_count_before = set([n.domainLedger.size for n in txnPoolNodeSet])
    assert len(txns_count_before) == 1, "Ledger size for nodes are not equal"
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def[0]
    revoc_req = build_revoc_def_by_default
    revoc_req['operation'][CRED_DEF_ID] = make_state_path_for_claim_def(author_did,
                                                                        str(claim_def_req['operation'][
                                                                                CLAIM_DEF_SCHEMA_REF]),
                                                                        claim_def_req['operation'][
                                                                            CLAIM_DEF_SIGNATURE_TYPE],
                                                                        claim_def_req['operation'][CLAIM_DEF_TAG]
                                                                        ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_req['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    txns_count_after = set([n.domainLedger.size for n in txnPoolNodeSet])
    assert len(txns_count_after) == 1, "Ledger size for nodes are not equal"
    # REVOC_REG_DEF transaction was written
    assert txns_count_after.pop() - txns_count_before.pop() == 1
