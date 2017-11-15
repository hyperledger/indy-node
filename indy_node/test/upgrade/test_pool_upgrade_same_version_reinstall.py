from copy import deepcopy

import pytest

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import codeVersion, checkUpgradeScheduled, \
    ensureUpgradeSent
from indy_common.constants import REINSTALL


def test_do_upgrade_to_the_same_version_if_reinstall(looper, tconf, nodeSet,
                                                     validUpgrade, trustee,
                                                     trusteeWallet):
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = codeVersion()
    upgr1[REINSTALL] = True

    # An upgrade scheduled, it should pass
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
