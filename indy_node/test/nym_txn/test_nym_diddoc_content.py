import copy

import pytest
from indy_node.test.mock import build_nym_request
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


def test_diddoc_content_added(
    looper, sdk_pool_handle, sdk_wallet_endorser, diddoc_content
):
    _, did = sdk_wallet_endorser
    nym_request = build_nym_request(did, did, None, diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])


def test_add_didoc_with_id_fails(
    looper, sdk_pool_handle, sdk_wallet_endorser, diddoc_content
):
    _, did = sdk_wallet_endorser
    diddoc_content_with_id = copy.deepcopy(diddoc_content)
    diddoc_content_with_id["id"] = "someId"
    nym_request = build_nym_request(did, did, None, diddoc_content_with_id, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [request_couple])
    e.match("InvalidClientRequest")
    e.match("diddocContent must not have `id` at root")
