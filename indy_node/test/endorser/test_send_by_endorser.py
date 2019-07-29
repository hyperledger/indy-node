import pytest
from indy_node.test.api.helper import sdk_write_schema_and_check, sdk_build_schema_request
from indy_node.test.endorser.helper import sdk_submit_and_check_by_endorser, sdk_append_request_endorser

from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.test.helper import sdk_multisign_request_object, sdk_get_and_check_replies, sdk_send_signed_requests


def test_send_by_endorser(looper, sdk_pool_handle, sdk_wallet_new_client, sdk_wallet_endorser):
    # try writing without Endorser by a None-role client
    with pytest.raises(RequestRejectedException):
        sdk_write_schema_and_check(looper, sdk_pool_handle, sdk_wallet_new_client,
                                   ["attr1", "attr2"], "name1", "1.0")

    # write with Endorser
    req_json = sdk_build_schema_request(looper, sdk_wallet_new_client,
                                        ["attr1", "attr2"], "name1", "1.0")
    sdk_submit_and_check_by_endorser(looper, sdk_pool_handle,
                                     sdk_wallet_author=sdk_wallet_new_client, sdk_wallet_endorser=sdk_wallet_endorser,
                                     request_json=req_json)


def test_both_author_and_endorser_must_sign(looper, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_endorser):
    '''
    Both author and endorser must sign the request even if the author can send the request without Endorser
    '''
    req_json = sdk_build_schema_request(looper, sdk_wallet_trustee,
                                        ["attr1", "attr2"], "name1", "2.0")
    req_json = sdk_append_request_endorser(looper, req_json, sdk_wallet_endorser[1])

    # sign by Author only
    req_json_author_only = sdk_multisign_request_object(looper, sdk_wallet_trustee, req_json)
    with pytest.raises(RequestNackedException):
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_author_only])[0]
        sdk_get_and_check_replies(looper, [request_couple])

    # sign by Endorser only
    req_json_endorser_only = sdk_multisign_request_object(looper, sdk_wallet_endorser, req_json)
    with pytest.raises(RequestNackedException):
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_endorser_only])[0]
        sdk_get_and_check_replies(looper, [request_couple])

    # sign by both
    req_json_both = sdk_multisign_request_object(looper, sdk_wallet_trustee, req_json)
    req_json_both = sdk_multisign_request_object(looper, sdk_wallet_endorser, req_json_both)
    request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_both])[0]
    sdk_get_and_check_replies(looper, [request_couple])
