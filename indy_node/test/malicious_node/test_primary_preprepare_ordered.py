import json

from plenum.common.request import Request

from plenum.common.constants import STEWARD_STRING, DOMAIN_LEDGER_ID, IDENTIFIER, TXN_PAYLOAD_PROTOCOL_VERSION, ROLE, \
    TXN_PAYLOAD_METADATA_REQ_ID

from plenum.test.pool_transactions.helper import prepare_nym_request, \
    sdk_add_new_nym

from plenum.common.util import randomString

from plenum.test.helper import sdk_sign_request_objects, sdk_send_signed_requests, \
    sdk_json_to_request_object, sdk_get_and_check_replies


def test_primary_preprepare_ordered(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    # Creating new steward
    seed = randomString(32)
    alias = randomString(5)
    wh, _ = sdk_wallet_trustee
    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(sdk_wallet_trustee, seed,
                            alias, STEWARD_STRING))
    nym_request = json.loads(nym_request)
    promoting_signed_reqs = sdk_sign_request_objects(looper, sdk_wallet_trustee,
                                                     [sdk_json_to_request_object(
                                                         nym_request)])
    request_couple = sdk_send_signed_requests(sdk_pool_handle, promoting_signed_reqs)[0]
    sdk_get_and_check_replies(looper, [request_couple])
    # Alpha is primary
    assert all(txnPoolNodeSet[0].name in n.master_replica.primaryName for n in txnPoolNodeSet)
    # new_did is steward
    assert txnPoolNodeSet[0].ledger_to_req_handler[1].idrCache.getNym(new_did)['role'] == '2'

    # Demote nym
    nym_request['operation']['role'] = None
    demoting_signed_reqs = sdk_sign_request_objects(looper, sdk_wallet_trustee,
                                                    [sdk_json_to_request_object(
                                                        nym_request)])
    request_couple = sdk_send_signed_requests(sdk_pool_handle, demoting_signed_reqs)[0]
    sdk_get_and_check_replies(looper, [request_couple])
    assert txnPoolNodeSet[0].ledger_to_req_handler[1].idrCache.getNym(new_did)['role'] is None

    # Primary revert nym's role to steward again
    promoting_signed_dict = json.loads(promoting_signed_reqs[0])
    req = Request(promoting_signed_dict[IDENTIFIER], promoting_signed_dict[TXN_PAYLOAD_METADATA_REQ_ID],
                  promoting_signed_dict['operation'], promoting_signed_dict['signature'],
                  protocolVersion=promoting_signed_dict[TXN_PAYLOAD_PROTOCOL_VERSION])
    for replica in list(txnPoolNodeSet[0].replicas._replicas.values()):
        replica.requestQueues[DOMAIN_LEDGER_ID].add(req.digest)
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    assert txnPoolNodeSet[0].ledger_to_req_handler[1].idrCache.getNym(new_did)[ROLE] == '2'
