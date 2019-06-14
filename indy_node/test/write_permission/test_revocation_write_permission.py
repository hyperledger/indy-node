import json
import pytest

from indy_common.constants import REVOKED, VALUE, PREV_ACCUM, CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG, ACCUM
from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.anon_creds.conftest import claim_def, build_revoc_reg_entry_for_given_revoc_reg_def, \
    build_revoc_def_by_default, build_revoc_def_by_endorser, build_revoc_def_by_steward, build_revoc_def_by_demand, \
    build_revoc_def_random
from indy_node.test.schema.test_send_get_schema import send_schema_seq_no
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check

from indy_node.test.schema.test_send_get_schema import send_schema_req


def create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc,
                         claim_def, wallet):
    # We need to have claim_def to send revocation txns

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


def create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc, claim_def, wallet):
    revoc_def_req = create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc,
                                         claim_def, wallet)

    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req = sdk_sign_request_from_dict(looper, wallet, rev_reg_entry)
    sdk_send_and_check([json.dumps(rev_entry_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    return rev_entry_req


def test_client_cant_create_revoc_reg_def(looper,
                                          txnPoolNodeSet,
                                          sdk_wallet_client,
                                          sdk_pool_handle,
                                          build_revoc_def_by_default,
                                          claim_def, tconf):
    with pytest.raises(RequestRejectedException):
        create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                             claim_def, sdk_wallet_client)


def test_allowed_roles_can_create_revoc_reg_def(looper,
                                                txnPoolNodeSet,
                                                sdk_wallet_trustee,
                                                sdk_wallet_endorser,
                                                sdk_wallet_steward,
                                                sdk_pool_handle,
                                                build_revoc_def_by_default,
                                                claim_def, tconf):
    # endorser
    create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                         claim_def, sdk_wallet_endorser)
    # steward
    create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                         claim_def, sdk_wallet_steward)
    # trustee
    create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                         claim_def, sdk_wallet_trustee)


def test_allowed_roles_can_send_revoc_reg_entry(looper,
                                                txnPoolNodeSet,
                                                sdk_wallet_trustee,
                                                sdk_wallet_endorser,
                                                sdk_wallet_steward,
                                                sdk_pool_handle,
                                                build_revoc_def_by_default,
                                                claim_def, tconf):
    # endorser
    create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                           build_revoc_def_by_default, claim_def, sdk_wallet_endorser)

    # steward

    create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                           build_revoc_def_by_default, claim_def, sdk_wallet_steward)

    # trustee
    create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle,
                         build_revoc_def_by_default, claim_def, sdk_wallet_trustee)


def test_client_not_owner_cant_create_revoc_reg_entry(looper,
                                                      txnPoolNodeSet,
                                                      sdk_wallet_trustee,
                                                      sdk_wallet_client,
                                                      sdk_pool_handle,
                                                      build_revoc_def_by_default,
                                                      claim_def, tconf):
    revoc_def_req_trustee = create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                                                 claim_def, sdk_wallet_trustee)

    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_trustee)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req_client = sdk_sign_request_from_dict(looper, sdk_wallet_client, rev_reg_entry)
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(rev_entry_req_client)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_endorser_not_owner_cant_create_revoc_reg_entry(looper,
                                                            txnPoolNodeSet,
                                                            sdk_wallet_trustee,
                                                            sdk_wallet_endorser,
                                                            sdk_pool_handle,
                                                            build_revoc_def_by_default,
                                                            claim_def, tconf):
    revoc_def_req_trustee = create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle, build_revoc_def_by_default,
                                                 claim_def, sdk_wallet_trustee)

    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_trustee)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req_endorser = sdk_sign_request_from_dict(looper, sdk_wallet_endorser, rev_reg_entry)
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(rev_entry_req_endorser)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_trustee_not_owner_cant_create_revoc_reg_entry(looper,
                                                       txnPoolNodeSet,
                                                       sdk_wallet_trustee,
                                                       sdk_wallet_steward,
                                                       sdk_pool_handle,
                                                       build_revoc_def_by_default,
                                                       claim_def, tconf):
    revoc_def_req_steward = create_revoc_reg_def(looper, txnPoolNodeSet, sdk_pool_handle,
                                                 build_revoc_def_by_default,
                                                 claim_def, sdk_wallet_steward)

    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req_steward)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req_trustee = sdk_sign_request_from_dict(looper, sdk_wallet_trustee, rev_reg_entry)
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(rev_entry_req_trustee)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_allowed_roles_can_edit_revoc_reg_entry(looper,
                                                txnPoolNodeSet,
                                                sdk_wallet_endorser,
                                                sdk_wallet_steward,
                                                sdk_wallet_trustee,
                                                sdk_pool_handle,
                                                build_revoc_def_by_default,
                                                build_revoc_def_by_endorser,
                                                build_revoc_def_by_steward,
                                                claim_def, tconf):
    # endorser
    revoc_entry_req_endorser = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                          build_revoc_def_by_endorser,
                                                          claim_def, sdk_wallet_endorser)

    revoc_entry_req_endorser['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_endorser['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_endorser['operation'][VALUE][
        ACCUM]
    revoc_entry_req_endorser['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_endorser = sdk_sign_request_from_dict(looper, sdk_wallet_endorser,
                                                              revoc_entry_req_endorser['operation'])

    sdk_send_and_check([json.dumps(revoc_entry_req_endorser)], looper, txnPoolNodeSet, sdk_pool_handle)

    # steward
    revoc_entry_req_trustee = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                     build_revoc_def_by_steward,
                                                     claim_def, sdk_wallet_steward)

    revoc_entry_req_trustee['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_trustee['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_trustee['operation'][VALUE][ACCUM]
    revoc_entry_req_trustee['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_trustee = sdk_sign_request_from_dict(looper, sdk_wallet_steward,
                                                         revoc_entry_req_trustee['operation'])

    sdk_send_and_check([json.dumps(revoc_entry_req_trustee)], looper, txnPoolNodeSet, sdk_pool_handle)

    # steward
    revoc_entry_req_steward = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                     build_revoc_def_by_default,
                                                     claim_def, sdk_wallet_trustee)

    revoc_entry_req_steward['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_steward['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_steward['operation'][VALUE][ACCUM]

    revoc_entry_req_steward['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_steward = sdk_sign_request_from_dict(looper, sdk_wallet_trustee,
                                                         revoc_entry_req_steward['operation'])

    sdk_send_and_check([json.dumps(revoc_entry_req_steward)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_not_owner_trustee_cant_edit_revoc_reg_entry(looper,
                                                     txnPoolNodeSet,
                                                     sdk_wallet_trustee,
                                                     sdk_wallet_endorser,
                                                     sdk_pool_handle,
                                                     build_revoc_def_by_demand,
                                                     claim_def, tconf):
    revoc_entry_req_steward = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                     build_revoc_def_by_demand,
                                                     claim_def, sdk_wallet_endorser)

    revoc_entry_req_steward['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_steward['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_steward['operation'][VALUE][ACCUM]

    revoc_entry_req_steward['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_steward = sdk_sign_request_from_dict(looper, sdk_wallet_trustee,
                                                         revoc_entry_req_steward['operation'])
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(revoc_entry_req_steward)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_not_owner_steward_cant_edit_revoc_reg_entry(looper,
                                                     txnPoolNodeSet,
                                                     sdk_wallet_steward,
                                                     sdk_wallet_endorser,
                                                     sdk_pool_handle,
                                                     build_revoc_def_by_steward,
                                                     claim_def, tconf):
    revoc_entry_req_steward = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                     build_revoc_def_by_steward,
                                                     claim_def, sdk_wallet_endorser)

    revoc_entry_req_steward['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_steward['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_steward['operation'][VALUE][ACCUM]

    revoc_entry_req_steward['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_steward = sdk_sign_request_from_dict(looper, sdk_wallet_steward,
                                                         revoc_entry_req_steward['operation'])
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(revoc_entry_req_steward)], looper, txnPoolNodeSet, sdk_pool_handle)


def test_not_owner_endorser_cant_edit_revoc_reg_entry(looper,
                                                          txnPoolNodeSet,
                                                          sdk_wallet_steward,
                                                          sdk_wallet_endorser,
                                                          sdk_pool_handle,
                                                          build_revoc_def_by_default,
                                                          claim_def, tconf):
    revoc_build = build_revoc_def_random(looper, sdk_wallet_steward)
    revoc_entry_req_steward = create_revoc_reg_entry(looper, txnPoolNodeSet, sdk_pool_handle,
                                                     revoc_build, claim_def, sdk_wallet_steward)

    revoc_entry_req_steward['operation'][VALUE][REVOKED] = [6, 7, 8]
    revoc_entry_req_steward['operation'][VALUE][PREV_ACCUM] = revoc_entry_req_steward['operation'][VALUE][ACCUM]

    revoc_entry_req_steward['operation'][VALUE][ACCUM] = randomString(10)
    revoc_entry_req_steward = sdk_sign_request_from_dict(looper, sdk_wallet_endorser,
                                                         revoc_entry_req_steward['operation'])
    with pytest.raises(RequestRejectedException):
        sdk_send_and_check([json.dumps(revoc_entry_req_steward)], looper, txnPoolNodeSet, sdk_pool_handle)
