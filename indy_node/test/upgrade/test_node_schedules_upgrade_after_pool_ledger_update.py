import pytest

from plenum.test.bls.helper import sdk_change_bls_key, check_bls_key


@pytest.fixture(scope="module")
def update_bls_keys(looper, tconf, nodeSet, sdk_pool_handle,
                    sdk_wallet_stewards):
    node = nodeSet[0]
    new_blspk = sdk_change_bls_key(looper, nodeSet, node,
                                   sdk_pool_handle, sdk_wallet_stewards[0],
                                   use_in_plenum=False)

    check_bls_key(new_blspk, node, nodeSet)


def test_node_schedules_upgrade_after_bls_keys_update(update_bls_keys,
                                                      upgradeScheduled):
    # Upgrade should work even after an update to the pool ledger with a
    # transaction that does not contain `SERVICES` field
    pass
