import copy
import json
import time
from random import randint

import pytest
from indy.did import create_and_store_my_did
from indy_common.constants import ENDORSER, NYM
from indy_node.test.mock import build_get_nym_request, build_nym_request
from plenum.common.exceptions import RequestNackedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request

diddoc_content = {
    "@context": [
        "https://www.w3.org/ns/did/v1",
        "https://identity.foundation/didcomm-messaging/service-endpoint/v1",
    ],
    "serviceEndpoint": [
        {
            "id": "did:indy:sovrin:123456#didcomm",
            "type": "didcomm-messaging",
            "serviceEndpoint": "https://example.com",
            "recipientKeys": ["#verkey"],
            "routingKeys": [],
        }
    ],
}


# Prepare nym with role endorser and no diddoc content
@pytest.fixture("module")
def prepare_endorser(looper, sdk_pool_handle, sdk_wallet_steward, sdk_wallet_endorser):
    _, did_steward = sdk_wallet_steward
    wh, _ = sdk_wallet_endorser
    seed = randomString(32)
    dest, verkey = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({"seed": seed}))
    )
    nym_request = build_nym_request(did_steward, dest, verkey, None, ENDORSER)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_steward, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])


# Add diddoc content to nym
@pytest.fixture("module")
def add_diddoc_content(looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser):
    _, did = sdk_wallet_endorser
    nym_request = build_nym_request(did, did, None, diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])


def test_diddoc_content_added(add_diddoc_content):
    pass


def test_get_nym_data_with_diddoc_content(
    looper, sdk_pool_handle, sdk_wallet_endorser, add_diddoc_content
):
    _, did = sdk_wallet_endorser
    get_nym_request = build_get_nym_request(did, did, None, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content
    )


def test_get_previous_nym_data_by_timestamp(
    looper, sdk_pool_handle, sdk_wallet_endorser, add_diddoc_content
):
    _, did = sdk_wallet_endorser
    # Get current nym data
    get_nym_request = build_get_nym_request(did, did, None, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])
    # Get timestamp from data
    timestamp = replies[0][1]["result"]["txnTime"]

    # Write new nym data
    new_diddoc_content = copy.deepcopy(diddoc_content)
    new_diddoc_content["serviceEndpoint"][0][
        "serviceEndpoint"
    ] = "https://new.example.com"

    time.sleep(3)

    nym_request = build_nym_request(did, did, None, new_diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])

    get_nym_request = build_get_nym_request(did, did, None, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == new_diddoc_content
    )

    update_ts = replies[0][1]["result"]["txnTime"]

    # Get previous nym data by exact timestamp
    get_nym_request = build_get_nym_request(did, did, timestamp, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content
    )

    # Get previous nym data by timestamp but not exact
    ts = randint(timestamp + 1, update_ts - 1)
    get_nym_request = build_get_nym_request(did, did, ts, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content
    )


def test_get_previous_nym_data_by_seq_no(
    looper, sdk_pool_handle, sdk_wallet_endorser, add_diddoc_content
):
    _, did = sdk_wallet_endorser
    # Get current nym data
    get_nym_request = build_get_nym_request(did, did, None, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])
    # Get seq_no from data
    seq_no = replies[0][1]["result"]["seqNo"]

    # Write new nym data
    new_diddoc_content = copy.deepcopy(diddoc_content)
    new_diddoc_content["serviceEndpoint"][0][
        "serviceEndpoint"
    ] = "https://new.example.com"

    time.sleep(3)

    nym_request = build_nym_request(did, did, None, new_diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])

    get_nym_request = build_get_nym_request(did, did, None, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == new_diddoc_content
    )

    # Get previous nym data by seq_no
    get_nym_request = build_get_nym_request(did, did, None, seq_no)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddoc_content"] == diddoc_content
    )


# Schema of NYM Tx in plenum is not enforced! Arbitrary properties can be injected, but won't be included in state
def test_add_arbitrary_property(
    looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser
):
    _, did = sdk_wallet_endorser

    nym_request = json.dumps(
        {
            "identifier": did,
            "reqId": randint(100, 1000000),
            "protocolVersion": 2,
            "operation": {"dest": did, "type": NYM, "someProp": "someValue"},
        }
    )

    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert replies[0][1]["result"]["txn"]["data"]["someProp"] == "someValue"


def test_add_diddoc_content_did_context_missing_fails(
    looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser
):
    _, did = sdk_wallet_endorser
    diddoc_content_without_did_context = copy.deepcopy(diddoc_content)
    diddoc_content_without_did_context["@context"] = [
        "https://identity.foundation/didcomm-messaging/service-endpoint/v1"
    ]
    nym_request = build_nym_request(
        did, did, None, diddoc_content_without_did_context, None
    )
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [request_couple])
    e.match("InvalidClientRequest")
    e.match("Invalid DIDDOC_Content")


def test_add_didoc_with_id_fails(
    looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser
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
    e.match("Invalid DIDDOC_Content")
