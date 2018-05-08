from copy import deepcopy

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import codeVersion, checkUpgradeScheduled, \
    sdk_ensure_upgrade_sent
from indy_common.constants import REINSTALL


def test_do_upgrade_to_the_same_version_if_reinstall(looper, tconf, nodeSet,
                                                     validUpgrade, sdk_pool_handle,
                                                     sdk_wallet_trustee):
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = codeVersion()
    upgr1[REINSTALL] = True

    # An upgrade scheduled, it should pass
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
