from copy import deepcopy

import pytest

from sovrin_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from sovrin_common.constants import REINSTALL

from sovrin_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    ensureUpgradeSent
from sovrin_node.server.upgrade_log import UpgradeLog

whitelist = ['Failed to upgrade node']


def test_upgrade_does_not_get_into_loop_if_reinstall_and_failed(looper, tconf, nodeSet,
                                             validUpgrade, trustee,
                                             trusteeWallet, monkeypatch):
    new_version = bumpedVersion()
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version
    upgr1[REINSTALL] = True

    # An upgrade scheduled, it should pass
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(eventually(checkUpgradeScheduled, nodeSet, upgr1[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))

    # we have not patched sovrin_node version so nodes think the upgrade had failed
    for node in nodeSet:
        # mimicking upgrade start
        node.upgrader._upgradeLog.appendStarted(0, node.upgrader.scheduledUpgrade[0], node.upgrader.scheduledUpgrade[2])
        node.notify_upgrade_start()
        # mimicking upgrader's initialization after restart
        node.upgrader.check_upgrade_succeeded()
        node.upgrader.scheduledUpgrade = None
        assert node.upgrader._upgradeLog.lastEvent[1] == UpgradeLog.UPGRADE_FAILED
        # mimicking node's catchup after restart
        node.postConfigLedgerCaughtUp()
        assert node.upgrader.scheduledUpgrade is None
        assert node.upgrader._upgradeLog.lastEvent[1] == UpgradeLog.UPGRADE_FAILED


