import pytest
from indy_common.constants import ENDORSER_STRING

from plenum.common.exceptions import RequestRejectedException

from plenum.test.pool_transactions.helper import sdk_add_new_nym


@pytest.mark.nym_txn
def test_steward_creates_a_endorser(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=ENDORSER_STRING)


@pytest.mark.nym_txn
# FIXME why is it necessary to check
def test_steward_creates_another_endorser(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=ENDORSER_STRING)
