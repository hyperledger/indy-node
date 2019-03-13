import json
import pytest

from indy_common.constants import REVOKED, VALUE, PREV_ACCUM, CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG
from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.anon_creds.conftest import claim_def, build_revoc_reg_entry_for_given_revoc_reg_def, \
    build_revoc_def_by_default, build_revoc_def_by_client, build_revoc_def_by_trust_anchor
from indy_node.test.schema.test_send_get_schema import send_schema_seq_no
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check


@pytest.fixture(scope='module')
def tconf(tconf):
    OLD_ANYONE_CAN_WRITE = tconf.ANYONE_CAN_WRITE
    tconf.ANYONE_CAN_WRITE = False

    yield tconf
    tconf.ANYONE_CAN_WRITE = OLD_ANYONE_CAN_WRITE


@pytest.fixture(scope="module")
def client_send_revoc_reg_def(looper,
                              txnPoolNodeSet,
                              sdk_wallet_client,
                              sdk_wallet_trust_anchor,
                              sdk_pool_handle,
                              build_revoc_def_by_default,
                              claim_def, tconf):
    # We need to have claim_def to send revocation txns
    # must be signed by trust anchor since ANYONE_CAN_WRITE is false

    claim_def_req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(claim_def_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    _, author_did = sdk_wallet_trust_anchor
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, revoc_reg['operation'])
    _, revoc_reply = sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]
    return revoc_req


def test_client_cant_send_revoc_reg_def(looper,
                                        txnPoolNodeSet,
                                        sdk_wallet_client,
                                        sdk_wallet_trust_anchor,
                                        sdk_pool_handle,
                                        build_revoc_def_by_client,
                                        claim_def, tconf):
    # when ANYONE_CAN_WRITE is false only trustee, steward, and trust_anchor can write

    claim_def_req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(claim_def_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    _, author_did = sdk_wallet_client
    revoc_reg = build_revoc_def_by_client
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_client, revoc_reg['operation'])
    with pytest.raises(RequestRejectedException):
        _, revoc_reply = sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]


def test_client_cant_send_revoc_reg_entry(looper,
                                         client_send_revoc_reg_def,
                                         sdk_wallet_client,
                                         txnPoolNodeSet,
                                         sdk_pool_handle):
    revoc_def_req = client_send_revoc_reg_def
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_client, rev_reg_entry)
    sdk_send_and_check([json.dumps(rev_entry_req)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_rev_reg_def_only_trustee_steward_trust_anchor_can_create():
    pass