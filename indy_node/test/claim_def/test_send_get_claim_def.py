import json
import pytest

from indy.anoncreds import issuer_create_and_store_credential_def
from indy.ledger import build_get_cred_def_request, build_cred_def_request

from plenum.common.exceptions import RequestNackedException
from plenum.common.constants import TXN_METADATA, TXN_METADATA_ID
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.helper import modify_field

from indy_node.test.claim_def.test_send_claim_def import schema_json


@pytest.fixture(scope="module")
def added_claim_def_id(looper, sdk_pool_handle, nodeSet,
                       sdk_wallet_trustee, schema_json):
    wallet_handle, identifier = sdk_wallet_trustee
    _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
        wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))
    request = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    return rep[0][1]['result'][TXN_METADATA][TXN_METADATA_ID]


def test_send_get_claim_def_succeeds(looper, sdk_pool_handle, nodeSet,
                                     sdk_wallet_trustee, added_claim_def_id):
    _, did = sdk_wallet_trustee
    request = looper.loop.run_until_complete(build_get_cred_def_request(did, added_claim_def_id))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])


def test_send_get_claim_def_as_client_succeeds(
        looper,
        sdk_pool_handle,
        nodeSet,
        added_claim_def_id,
        sdk_wallet_client):
    _, did = sdk_wallet_client
    request = looper.loop.run_until_complete(build_get_cred_def_request(did, added_claim_def_id))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])


def test_send_get_claim_def_with_invalid_ref_fails(looper, sdk_pool_handle, nodeSet,
                                                   sdk_wallet_trustee, added_claim_def_id):
    _, did = sdk_wallet_trustee
    request = looper.loop.run_until_complete(build_get_cred_def_request(did, added_claim_def_id))
    request = modify_field(request, '!@#', 'operation', 'ref')
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('expected types \'int\', got \'str\'')


def test_send_get_claim_def_with_invalid_signature_not_get_claim(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, added_claim_def_id):
    _, did = sdk_wallet_trustee
    request = looper.loop.run_until_complete(build_get_cred_def_request(did, added_claim_def_id))
    request = modify_field(request, 'ABC', 'operation', 'signature_type')
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['data'] is None
