import json
import pytest

from indy_common.constants import CRED_DEF_ID, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG, VALUE, \
    REVOKED, PREV_ACCUM
from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.helper import sdk_add_attribute_and_check
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check, \
    sdk_get_and_check_replies, sdk_sign_and_submit_req
from plenum.common.exceptions import RequestRejectedException

from indy_common.auth import Authoriser
from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request

from indy_node.test.anon_creds.conftest import claim_def, build_revoc_reg_entry_for_given_revoc_reg_def
from indy_node.test.attrib_txn.test_nym_attrib import attributeData, attributeName, attributeValue
from indy_node.test.anon_creds.conftest import build_revoc_def_by_default

from indy_node.test.schema.test_send_get_schema import send_schema_seq_no


@pytest.fixture(scope="module")
def tconf(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_ANYONE_CAN_WRITE = tconf.ANYONE_CAN_WRITE
    tconf.ANYONE_CAN_WRITE = True

    yield tconf

    tconf.ANYONE_CAN_WRITE = OLD_ANYONE_CAN_WRITE
    Authoriser.auth_map = None


def test_client_can_send_nym(looper,
                             sdk_wallet_client,
                             sdk_wallet_trust_anchor,
                             sdk_pool_handle):
    # Trust anchor can create schema in any case
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trust_anchor)

    # Client can create another client NYM when ANYONE_CAN_WRITE set to True
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_client)


def test_client_can_send_attrib(looper,
                                sdk_wallet_client,
                                sdk_wallet_trust_anchor,
                                sdk_pool_handle,
                                attributeData):
    _, client_did = sdk_wallet_client

    # Client as an owner can add attribute to his NYM
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_client,
                                attributeData, client_did)

    # another client or trust anchor cannot add attribute to another NYM
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trust_anchor,
                                    attributeData, client_did)
    assert e.match('can not touch raw field since only the owner can modify it')


def test_client_can_send_schema(looper,
                                sdk_wallet_client,
                                sdk_wallet_trust_anchor,
                                sdk_pool_handle):
    # Trust anchor can create schema in any case
    _, identifier = sdk_wallet_trust_anchor
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "name", "1.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trust_anchor, request)])

    # Client can create schema if ANYONE_CAN_WRITE flag set to False
    _, identifier = sdk_wallet_client
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "name", "1.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])


def test_client_can_send_claim_def(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_client,
                                   sdk_wallet_trust_anchor,
                                   sdk_pool_handle,
                                   claim_def):
    # Trust anchor can create claim_def in any case
    req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # Client can create claim_def if ANYONE_CAN_WRITE flag set to False
    req = sdk_sign_request_from_dict(looper, sdk_wallet_client, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)


@pytest.fixture(scope="module")
def client_send_revoc_reg_def(looper,
                              txnPoolNodeSet,
                              sdk_wallet_client,
                              sdk_pool_handle,
                              build_revoc_def_by_default,
                              claim_def):
    claim_def_req = sdk_sign_request_from_dict(looper, sdk_wallet_client, claim_def)
    sdk_send_and_check([json.dumps(claim_def_req)], looper, txnPoolNodeSet, sdk_pool_handle)

    _, author_did = sdk_wallet_client
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_client, revoc_reg['operation'])
    _, revoc_reply = sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]
    return revoc_req


def test_client_can_send_revoc_reg_def(client_send_revoc_reg_def):
    pass


def test_client_can_send_revoc_reg_entry(looper,
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
