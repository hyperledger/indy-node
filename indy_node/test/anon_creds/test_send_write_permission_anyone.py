import json
import pytest
from indy_node.test.helper import sdk_add_attribute_and_check
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check, \
    sdk_get_and_check_replies, sdk_sign_and_submit_req
from plenum.common.exceptions import RequestRejectedException

from indy_common.auth import Authoriser
from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request

from indy_node.test.anon_creds.conftest import claim_def
from indy_client.test.test_nym_attrib import attributeData, attributeName, attributeValue


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
                             txnPoolNodeSet,
                             sdk_wallet_client,
                             sdk_wallet_trust_anchor,
                             sdk_pool_handle,
                             attributeData):
    # client can create another client NYM when ANYONE_CAN_WRITE set to True
    sdk_new_client_wallet = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_client)
    _, new_client_did = sdk_new_client_wallet

    # client as an owner can add attribute to his NYM
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_new_client_wallet,
                                attributeData, new_client_did)

    # another client or trust anchor cannot add attribute to another NYM
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trust_anchor,
                                    attributeData, new_client_did)
    assert e.match('Only identity owner/guardian can add attribute for that identity')

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_client,
                                    attributeData, new_client_did)
    assert e.match('Only identity owner/guardian can add attribute for that identity')


def test_client_can_send_schema(looper,
                                txnPoolNodeSet,
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
