import pytest

from plenum.common.exceptions import RequestNackedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent


def test_forced_request_validation(looper, txnPoolNodeSet,
                                   sdk_pool_handle, sdk_wallet_steward,
                                   sdk_wallet_trustee, validUpgradeExpForceTrue):
    for node in txnPoolNodeSet[2:]:
        node.upgrader.check_upgrade_possible = lambda a, b, c: None
    for node in txnPoolNodeSet[:2]:
        node.upgrader.check_upgrade_possible = lambda a, b, c: 'some exception'

    with pytest.raises(RequestNackedException, match='some exception'):
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, validUpgradeExpForceTrue)

    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward)
