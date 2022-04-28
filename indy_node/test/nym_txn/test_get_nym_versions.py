import copy
import json
import time
from random import randint

import pytest
from indy_common.constants import NYM_VERSION_CONVENTION
from indy_node.test.helper import sdk_send_and_check_req_json
from indy_node.test.mock import build_get_nym_request, build_nym_request
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


def test_get_nym_data_with_diddoc_content_without_seq_no_or_timestamp(
    looper, sdk_pool_handle, sdk_wallet_endorser_factory, diddoc_content, diddoc_content_json
):
    sdk_wallet_endorser = sdk_wallet_endorser_factory(diddoc_content)
    _, did = sdk_wallet_endorser
    get_nym_request = build_get_nym_request(did, did)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == diddoc_content_json
    )


def test_get_previous_nym_data_by_timestamp(
    looper, sdk_pool_handle, sdk_wallet_endorser_factory, diddoc_content, diddoc_content_json
):
    sdk_wallet_endorser = sdk_wallet_endorser_factory(diddoc_content)
    _, did = sdk_wallet_endorser

    # Get current nym data
    get_nym_request = build_get_nym_request(did, did)
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
    new_diddoc_content = json.dumps(new_diddoc_content)

    time.sleep(3)

    nym_request = build_nym_request(
        identifier=did, dest=did, diddoc_content=new_diddoc_content
    )
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])

    get_nym_request = build_get_nym_request(did, did)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == new_diddoc_content
    )

    update_ts = replies[0][1]["result"]["txnTime"]

    # Get previous nym data by exact timestamp
    get_nym_request = build_get_nym_request(did, did, timestamp)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == diddoc_content_json
    )

    # Get previous nym data by timestamp but not exact
    ts = randint(timestamp + 1, update_ts - 1)
    get_nym_request = build_get_nym_request(did, did, ts)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == diddoc_content_json
    )


def test_get_previous_nym_data_by_seq_no(
    looper, sdk_pool_handle, sdk_wallet_endorser_factory, diddoc_content, diddoc_content_json
):
    sdk_wallet_endorser = sdk_wallet_endorser_factory(diddoc_content)
    _, did = sdk_wallet_endorser

    # Get current nym data
    get_nym_request = build_get_nym_request(did, did)
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
    new_diddoc_content = json.dumps(new_diddoc_content)

    time.sleep(3)

    nym_request = build_nym_request(did, did, None, new_diddoc_content, None)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, nym_request
    )
    sdk_get_and_check_replies(looper, [request_couple])

    get_nym_request = build_get_nym_request(did, did)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == new_diddoc_content
    )

    # Get previous nym data by seq_no
    get_nym_request = build_get_nym_request(did, did, seq_no=seq_no)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        json.loads(replies[0][1]["result"]["data"])["diddocContent"] == diddoc_content_json
    )


def test_nym_txn_rejected_with_both_seqNo_and_timestamp(
    looper, sdk_pool_handle, sdk_wallet_endorser
):
    _, did = sdk_wallet_endorser

    # Attempt to get previous nym data by exact timestamp and seqNo
    get_nym_request = build_get_nym_request(did, did, int(time.time()), 10)

    with pytest.raises(RequestNackedException) as e:
        sdk_send_and_check_req_json(
            looper, sdk_pool_handle, sdk_wallet_endorser, get_nym_request
        )
    e.match("InvalidClientRequest")
    e.match("client request invalid")
    e.match("mutually exclusive")


def test_get_nym_returns_no_nym_version_when_absent(
    looper, sdk_pool_handle, sdk_wallet_endorser
):
    _, did = sdk_wallet_endorser
    get_nym_request = build_get_nym_request(did, did)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    assert (
        "version" not in json.loads(replies[0][1]["result"]["data"])
    )


def test_get_nym_returns_nym_version_when_set(
    looper, sdk_pool_handle, sdk_wallet_endorser_factory
):
    sdk_wallet_endorser = sdk_wallet_endorser_factory(version=NYM_VERSION_CONVENTION)
    _, did = sdk_wallet_endorser
    get_nym_request = build_get_nym_request(did, did)
    request_couple = sdk_sign_and_send_prepared_request(
        looper, sdk_wallet_endorser, sdk_pool_handle, get_nym_request
    )
    replies = sdk_get_and_check_replies(looper, [request_couple])

    returned = json.loads(replies[0][1]["result"]["data"])
    assert "version" in returned
    assert returned["version"] == NYM_VERSION_CONVENTION
