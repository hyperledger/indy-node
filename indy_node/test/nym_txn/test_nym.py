import pytest
from indy_common.constants import TRUST_ANCHOR_STRING

from plenum.common.exceptions import RequestRejectedException

from plenum.test.pool_transactions.helper import sdk_add_new_nym


def testStewardCreatesATrustAnchor(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=TRUST_ANCHOR_STRING)


# FIXME why is it necessary to check
def testStewardCreatesAnotherTrustAnchor(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=TRUST_ANCHOR_STRING)
