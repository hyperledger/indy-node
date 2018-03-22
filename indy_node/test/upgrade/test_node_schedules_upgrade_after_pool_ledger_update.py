import pytest

from plenum.test.bls.helper import change_bls_key, check_bls_key
from plenum.test.conftest import pool_txn_stewards_data, stewards_and_wallets


@pytest.fixture(scope="module")
def update_bls_keys(looper, tconf, nodeSet, stewards_and_wallets):
    node = nodeSet[0]
    steward_client, steward_wallet = stewards_and_wallets[0]
    new_blspk = change_bls_key(looper, nodeSet, node,
                               steward_client, steward_wallet)

    check_bls_key(new_blspk, node, nodeSet)


def test_node_schedules_upgrade_after_bls_keys_update(update_bls_keys,
                                                      upgradeScheduled):
    # Upgrade should work even after an update to the pool ledger with a
    # transaction that does not contain `SERVICES` field
    pass
