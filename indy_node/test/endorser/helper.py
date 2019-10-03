from indy.ledger import append_request_endorser

from plenum.test.helper import sdk_get_and_check_replies, sdk_send_signed_requests, sdk_multisign_request_object


def sdk_append_request_endorser(
        looper,
        request_json,
        endorser_did):
    return looper.loop.run_until_complete(append_request_endorser(request_json, endorser_did))


def sdk_submit_and_check_by_endorser(looper, sdk_pool_handle, sdk_wallet_author, sdk_wallet_endorser, request_json):
    _, endorser_did = sdk_wallet_endorser

    # 1. append Endorser field
    request_json = sdk_append_request_endorser(looper, request_json, endorser_did)

    # 2. sign by both Author and Endorser
    request_json = sdk_multisign_request_object(looper, sdk_wallet_author, request_json)
    request_json = sdk_multisign_request_object(looper, sdk_wallet_endorser, request_json)

    # 3. submit by Endorser
    request_couple = sdk_send_signed_requests(sdk_pool_handle, [request_json])[0]
    sdk_get_and_check_replies(looper, [request_couple])
