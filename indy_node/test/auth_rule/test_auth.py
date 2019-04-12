import json

from indy_node.test.auth_rule.helper import add_new_nym
from plenum.common.constants import STEWARD_STRING
from plenum.test.helper import sdk_send_signed_requests, \
    sdk_get_and_check_replies, sdk_multi_sign_request_objects, sdk_json_to_request_object

from plenum.common.util import hexToFriendly
from plenum.test.pool_transactions.helper import prepare_node_request, prepare_nym_request


def test_send_same_txn_with_different_signatures_in_separate_batches(
        looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_client):
    # Send two txn with same payload digest but different signatures,
    # so that they could be processed in one batch, trying to break the ledger hashes

    wh, did = sdk_wallet_trustee

    add_new_nym(looper,
                sdk_pool_handle,
                [sdk_wallet_client],
                'newSteward1',
                STEWARD_STRING,
                dest=did)