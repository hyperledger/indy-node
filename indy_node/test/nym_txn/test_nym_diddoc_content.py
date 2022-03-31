import copy
import json
from random import randint

import pytest
from indy_common.constants import NYM
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


# Schema of NYM Tx in plenum is not enforced! Arbitrary properties can be injected, but won't be included in state
def test_add_arbitrary_property(
    looper, sdk_pool_handle, sdk_wallet_endorser
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
    e.match("Invalid DIDDOC_Content")
