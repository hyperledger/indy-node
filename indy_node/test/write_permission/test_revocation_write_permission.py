import json
import pytest

from indy_common.constants import REVOKED, VALUE, PREV_ACCUM, CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG
from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.anon_creds.conftest import claim_def, build_revoc_reg_entry_for_given_revoc_reg_def, \
    build_revoc_def_by_default, build_revoc_def_by_trust_anchor
from indy_node.test.schema.test_send_get_schema import send_schema_seq_no
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check


@pytest.fixture(scope='module')
def tconf(tconf):
    OLD_ANYONE_CAN_WRITE = tconf.ANYONE_CAN_WRITE
    tconf.ANYONE_CAN_WRITE = False

    yield tconf
    tconf.ANYONE_CAN_WRITE = OLD_ANYONE_CAN_WRITE


def send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc,
                       claim_def, wallet):
    # We need to have claim_def to send revocation txns
    # must be signed by trust anchor since ANYONE_CAN_WRITE is false

    claim_def_req = sdk_sign_request_from_dict(looper, wallet, claim_def)
    sdk_send_and_check([json.dumps(claim_def_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    _, author_did = wallet
    revoc_reg = build_revoc
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, wallet, revoc_reg['operation'])
    _, revoc_reply = sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]
    return revoc_req


def test_client_cant_send_revoc_reg_def(looper,
                                        txnPoolNodeSet,
                                        sdk_wallet_client,
                                        sdk_pool_handle,
                                        build_revoc_def_by_default,
                                        claim_def, tconf):
    with pytest.raises(RequestRejectedException):
        send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                           claim_def, sdk_wallet_client)


def test_allowed_roles_can_send_revoc_reg_def(looper,
                                              txnPoolNodeSet,
                                              sdk_wallet_trustee,
                                              sdk_wallet_trust_anchor,
                                              sdk_wallet_steward,
                                              sdk_pool_handle,
                                              build_revoc_def_by_default,
                                              claim_def, tconf):
    # trust anchor
    send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                       claim_def, sdk_wallet_trust_anchor)
    # steward
    send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                       claim_def, sdk_wallet_steward)
    # trustee
    send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                       claim_def, sdk_wallet_trustee)


def test_allowed_roles_can_send_revoc_reg_entry(looper,
                                                txnPoolNodeSet,
                                                sdk_wallet_trustee,
                                                sdk_wallet_trust_anchor,
                                                sdk_wallet_steward,
                                                sdk_pool_handle,
                                                build_revoc_def_by_default,
                                                claim_def, tconf):
    # trust anchor
    revoc_def_req_trust_anchor = send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                                                    claim_def, sdk_wallet_trust_anchor)

    rev_reg_entry_trust_anchor = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_trust_anchor)
    rev_reg_entry_trust_anchor[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry_trust_anchor[VALUE][PREV_ACCUM]
    rev_entry_req_trust_anchor = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, rev_reg_entry_trust_anchor)
    sdk_send_and_check([json.dumps(rev_entry_req_trust_anchor)], looper, txnPoolNodeSet, sdk_pool_handle)

    # steward
    revoc_def_req_steward = send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle,
                                               build_revoc_def_by_default, claim_def, sdk_wallet_steward)
    rev_reg_entry_steward = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_steward)
    rev_reg_entry_steward[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry_steward[VALUE][PREV_ACCUM]
    rev_entry_req_steward = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry_steward)
    sdk_send_and_check([json.dumps(rev_entry_req_steward)], looper, txnPoolNodeSet, sdk_pool_handle)

    # trustee
    revoc_def_req_trustee = send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle,
                                               build_revoc_def_by_default, claim_def, sdk_wallet_trustee)

    rev_reg_entry_trustee = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_trustee)
    rev_reg_entry_trustee[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry_trustee[VALUE][PREV_ACCUM]
    rev_entry_req_trustee = sdk_sign_request_from_dict(looper, sdk_wallet_trustee, rev_reg_entry_trustee)
    sdk_send_and_check([json.dumps(rev_entry_req_trustee)], looper, txnPoolNodeSet, sdk_pool_handle)

test_not_owner_cant_create_revoc_reg_entry
def (looper,
                                               txnPoolNodeSet,
                                               sdk_wallet_trustee,
                                               sdk_wallet_client,
                                               sdk_pool_handle,
                                               build_revoc_def_by_default,
                                               claim_def, tconf):

    send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                       claim_def, sdk_wallet_trustee)

    # trust anchor
    revoc_def_req_trust_anchor = send_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                                                    claim_def, sdk_wallet_client)

    rev_reg_entry_trust_anchor = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_trust_anchor)
    rev_reg_entry_trust_anchor[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry_trust_anchor[VALUE][PREV_ACCUM]
    rev_entry_req_trust_anchor = sdk_sign_request_from_dict(looper, sdk_wallet_client, rev_reg_entry_trust_anchor)
    sdk_send_and_check([json.dumps(rev_entry_req_trust_anchor)], looper, txnPoolNodeSet, sdk_pool_handle)



