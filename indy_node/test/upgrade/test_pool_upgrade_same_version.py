from copy import deepcopy

import pytest

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import codeVersion, checkUpgradeScheduled, \
    sdk_ensure_upgrade_sent


def test_do_not_upgrade_to_the_same_version(looper, tconf, nodeSet,
                                            validUpgrade, sdk_pool_handle,
                                            sdk_wallet_trustee):
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = codeVersion()

    # An upgrade is not scheduled
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgr1)
    with pytest.raises(AssertionError):
        looper.run(
            eventually(
                checkUpgradeScheduled,
                nodeSet,
                upgr1[VERSION],
                retryWait=1,
                timeout=waits.expectedUpgradeScheduled()))
