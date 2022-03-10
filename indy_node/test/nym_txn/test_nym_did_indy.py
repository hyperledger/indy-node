import copy
import json
from random import randint

import pytest
from indy.did import create_and_store_my_did
from indy_common.constants import ENDORSER, NYM
from indy_node.test.mock import build_nym_request
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
diddoc_content_json = json.dumps(diddoc_content)


# Prepare nym with role endorser and no diddoc content
@pytest.fixture(scope="module")
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
@pytest.fixture(scope="module")
def add_diddoc_content(looper, sdk_pool_handle, sdk_wallet_endorser, prepare_endorser):
    _, did = sdk_wallet_endorser
    nym_request = build_nym_request(did, did, None, diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])


def test_diddoc_content_added(add_diddoc_content):
    pass


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
