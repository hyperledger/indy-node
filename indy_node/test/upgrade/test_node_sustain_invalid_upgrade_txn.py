import pytest

from indy_node.test.upgrade.conftest import EXT_PKT_NAME, EXT_PKT_VERSION
from plenum.common.exceptions import RequestNackedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent


@pytest.fixture
def pckg(request):
    return EXT_PKT_NAME, EXT_PKT_VERSION


def test_forced_request_validation(looper, txnPoolNodeSet,
                                   sdk_pool_handle, sdk_wallet_steward,
                                   sdk_wallet_trustee, validUpgradeExpForceTrue):
    for node in txnPoolNodeSet[2:]:
        node.upgrader.check_upgrade_possible = lambda a, b, c: None
    for node in txnPoolNodeSet[:2]:
        node.upgrader.check_upgrade_possible = lambda a, b, c: 'some exception'

    assert all(n.spylog.getAll('processPropagate') == [] for n in txnPoolNodeSet)

    with pytest.raises(RequestNackedException, match='some exception'):
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, validUpgradeExpForceTrue)

    assert all(len(n.spylog.getAll('processPropagate')) == 2 for n in txnPoolNodeSet[:2])
    assert all(len(n.spylog.getAll('processPropagate')) == 1 for n in txnPoolNodeSet[2:])

    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward)
