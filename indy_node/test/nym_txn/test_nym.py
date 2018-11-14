import pytest
from indy_common.constants import TRUST_ANCHOR_STRING

from plenum.common.exceptions import RequestRejectedException

from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_non_steward_cannot_create_trust_anchor(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_wallet_client = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_client, role=TRUST_ANCHOR_STRING)
    e.match('None role cannot')


def testStewardCreatesATrustAnchor(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=TRUST_ANCHOR_STRING)


def testStewardCreatesAnotherTrustAnchor(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=TRUST_ANCHOR_STRING)


def test_non_trust_anchor_cannot_create_user(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_wallet_client = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_client)
    e.match('None role cannot')


def testTrustAnchorCreatesAUser(sdk_user_wallet_a):
    pass
