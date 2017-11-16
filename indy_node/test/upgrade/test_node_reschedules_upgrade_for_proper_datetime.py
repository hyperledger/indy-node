from copy import deepcopy

import dateutil
from datetime import timedelta

from indy_common.constants import SHA256, SCHEDULE
from indy_node.test import waits
from indy_node.test.upgrade.helper import bumpVersion, checkUpgradeScheduled, \
    ensureUpgradeSent
from plenum.common.constants import VERSION, NAME
from plenum.common.util import randomString
from stp_core.loop.eventually import eventually


def test_node_reschedules_upgrade_for_proper_datetime(
        looper, tconf, nodeSet, validUpgrade, trustee, trusteeWallet):

    upgr1 = deepcopy(validUpgrade)
    # Upgrade 1 of each node will be scheduled for tomorrow
    for nodeId in upgr1[SCHEDULE]:
        nodeUpgradeDateTime = dateutil.parser.parse(upgr1[SCHEDULE][nodeId])
        nodeUpgradeDateTime += timedelta(days=1)
        upgr1[SCHEDULE][nodeId] = nodeUpgradeDateTime.isoformat()

    upgr2 = deepcopy(upgr1)
    upgr2[VERSION] = bumpVersion(upgr1[VERSION])
    upgr2[NAME] += randomString(32)
    upgr2[SHA256] = 'ef9c3984e7a31994d4f692139116120bd0dd1ff7e270b6a2d773f8f2f9214d4c'
    # Upgrade 2 of each node will be scheduled for its own day
    # (since today with one day step)
    deltaDays = -1
    for nodeId in upgr2[SCHEDULE]:
        nodeUpgradeDateTime = dateutil.parser.parse(upgr2[SCHEDULE][nodeId])
        nodeUpgradeDateTime += timedelta(days=deltaDays)
        upgr2[SCHEDULE][nodeId] = nodeUpgradeDateTime.isoformat()
        deltaDays += 1

    # Upgrade 1 is scheduled
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))

    # Upgrade 2 cancels Upgrade 1 and is scheduled itself
    # according its own schedule
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr2)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr2[VERSION],
            upgr2[SCHEDULE],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
