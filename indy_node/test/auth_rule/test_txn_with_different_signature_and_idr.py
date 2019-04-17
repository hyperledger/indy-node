import json
import pytest

from plenum.common.constants import STEWARD_STRING
from plenum.common.exceptions import RequestNackedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_multi_sign_request_objects, \
    sdk_json_to_request_object, sdk_send_signed_requests, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import prepare_nym_request


def test_txn_with_different_signature_and_idr(
        looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_client):
    # filling nym request and getting steward did
    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(sdk_wallet_trustee, randomString(32),
                            'newSteward1', STEWARD_STRING))

    # sending request using 'sdk_' functions
    signed_reqs = sdk_multi_sign_request_objects(looper, [sdk_wallet_client],
                                                 [sdk_json_to_request_object(
                                                     json.loads(nym_request))])
    request_couple = sdk_send_signed_requests(sdk_pool_handle, signed_reqs)[0]

    with pytest.raises(RequestNackedException, match="The identifier is not contained in signatures"):
        # waiting for replies
        sdk_get_and_check_replies(looper, [request_couple])
