from copy import deepcopy

import dateutil
from datetime import timedelta

from indy_common.constants import SCHEDULE
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled, \
    ensureUpgradeSent
from plenum.common.constants import VERSION
from stp_core.loop.eventually import eventually


def test_node_schedules_upgrade_for_proper_datetime(
        looper, tconf, nodeSet, validUpgrade, trustee, trusteeWallet):

    upgr1 = deepcopy(validUpgrade)
    # Upgrade of each node will be scheduled for its own day
    # (since today with one day step)
    deltaDays = 0
    for nodeId in upgr1[SCHEDULE]:
        nodeUpgradeDateTime = dateutil.parser.parse(upgr1[SCHEDULE][nodeId])
        nodeUpgradeDateTime += timedelta(days=deltaDays)
        upgr1[SCHEDULE][nodeId] = nodeUpgradeDateTime.isoformat()
        deltaDays += 1

    # Upgrade is scheduled for the proper datetime for each node
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            upgr1[SCHEDULE],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
