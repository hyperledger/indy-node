from copy import deepcopy

import pytest

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from indy_common.constants import FORCE

from indy_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    ensureUpgradeSent, check_no_loop
from indy_node.server.upgrade_log import UpgradeLog

whitelist = ['Failed to upgrade node',
             'failed upgrade',
             'This problem may have external reasons, check syslog for more information']


def test_upgrade_does_not_get_into_loop_force_if_failed(
        looper, tconf, nodeSet, validUpgrade, trustee, trusteeWallet, monkeypatch):
    new_version = bumpedVersion()
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version
    upgr1[FORCE] = True

    # An upgrade scheduled, it should pass
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))

    # we have not patched indy_node version so nodes think the upgrade had
    # failed
    check_no_loop(nodeSet, UpgradeLog.UPGRADE_FAILED)
