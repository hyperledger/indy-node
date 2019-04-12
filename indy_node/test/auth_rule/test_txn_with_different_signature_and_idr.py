import pytest

from indy_node.test.auth_rule.helper import add_new_nym
from plenum.common.constants import STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException


def test_send_same_txn_with_different_signatures_in_separate_batches(
        looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_client):

    wh, did = sdk_wallet_trustee
    with pytest.raises(RequestRejectedException, match="Not enough TRUSTEE signatures"):
        add_new_nym(looper,
                    sdk_pool_handle,
                    [sdk_wallet_client],
                    'newSteward1',
                    STEWARD_STRING,
                    dest=did)
