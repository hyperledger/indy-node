import json
import copy

import pytest
from indy.did import create_and_store_my_did
from indy_node.test.helper import sdk_add_attribute_and_check
from indy_node.test.mock import build_nym_request, build_get_nym_request
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import (
    sdk_sign_and_send_prepared_request,
)


diddoc_content = {
    "@context": [
        "https://www.w3.org/ns/did/v1",
        "https://identity.foundation/didcomm-messaging/service-endpoint/v1",
    ],
    "serviceEndpoint": [{
        "id": "did:indy:sovrin:123456#didcomm",
        "type": "didcomm-messaging",
        "serviceEndpoint": "https://example.com",
        "recipientKeys": ["#verkey"],
        "routingKeys": [],
    }],
}


# Prepare nym with role endorser and no diddoc content
@pytest.fixture("module")
def prepare_endorser(looper, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_endorser):
    wh_trustee, did_trustee = sdk_wallet_trustee
    wh, _ = sdk_wallet_endorser
    seed = randomString(32)
    dest, verkey = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({"seed": seed}))
    )
    # Role = 2 == ENDORSER
    nym_request = build_nym_request(did_trustee, dest, verkey, None, "2")
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [request_couple])


# Add diddoc content to nym
@pytest.fixture("module")
def add_diddoc_content(looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser):
    wh, did = sdk_wallet_endorser
    nym_request = build_nym_request(did, did, None, diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [request_couple])


def test_diddoc_content_added(add_diddoc_content):
    pass


def test_get_nym_data_with_diddoc_content(looper, sdk_pool_handle, sdk_wallet_endorser, add_diddoc_content):
    wh, did = sdk_wallet_endorser
    get_nym_request = build_get_nym_request(did, did, None)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request)
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content


def test_get_previous_nym_data_by_timestamp(looper, sdk_pool_handle, sdk_wallet_endorser, add_diddoc_content):
    wh, did = sdk_wallet_endorser
    # Get current nym data
    get_nym_request = build_get_nym_request(did, did, None)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request)
    replies = sdk_get_and_check_replies(looper, [request_couple])
    # Get timestamp from data
    timestamp = replies[0][1]["result"]["txnTime"]

    # Write new nym data
    new_diddoc_content = copy.deepcopy(diddoc_content)
    new_diddoc_content["serviceEndpoint"][0]["serviceEndpoint"] = "https://new.example.com"

    nym_request = build_nym_request(did, did, None, new_diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [request_couple])

    # Get new nym data
    get_nym_request = build_get_nym_request(did, did, None)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request)
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == new_diddoc_content

    # Get previous nym data by timestamp
    get_nym_request = build_get_nym_request(did, did, timestamp)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request)
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content
