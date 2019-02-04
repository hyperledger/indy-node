from indy_node.test import waits
from plenum.test.pool_transactions.helper import demote_node
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from indy_common.constants import SCHEDULE
from indy_node.test.upgrade.helper import checkUpgradeScheduled, sdk_ensure_upgrade_sent


def test_update_with_demoted_node(looper, nodeSet, validUpgrade,
                                  sdk_pool_handle, sdk_wallet_stewards,
                                  sdk_wallet_trustee):
    # demote one node
    demote_node(looper, sdk_wallet_stewards[3], sdk_pool_handle, nodeSet[3])

    # remove demoted node from upgrade schedule
    upgr = validUpgrade
    del upgr[SCHEDULE][nodeSet[3].id]

    # send upgrade
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, upgr)

    # check upg scheduled
    looper.run(eventually(checkUpgradeScheduled, nodeSet[:3], upgr[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
