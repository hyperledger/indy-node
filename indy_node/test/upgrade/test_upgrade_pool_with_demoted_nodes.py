from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import ALIAS, SERVICES, VERSION
from indy_common.constants import SCHEDULE
from indy_node.test.upgrade.helper import ensureUpgradeSent, checkUpgradeScheduled

from plenum.test.pool_transactions.helper import updateNodeData
from plenum.test.conftest import pool_txn_stewards_data, stewards_and_wallets


def test_update_with_demoted_node(looper, nodeSet, validUpgrade,
                                  stewards_and_wallets, trustee, trusteeWallet):
    # demote one node
    node_steward_cl, steward_wallet = stewards_and_wallets[3]
    node_data = {
        ALIAS: nodeSet[3].name,
        SERVICES: []
    }
    updateNodeData(looper, node_steward_cl, steward_wallet, nodeSet[3], node_data)

    # remove demoted node from upgrade schedule
    upgr = validUpgrade
    del upgr[SCHEDULE][nodeSet[3].id]

    # send upgrade
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr)

    # check upg scheduled
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:3], upgr[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
