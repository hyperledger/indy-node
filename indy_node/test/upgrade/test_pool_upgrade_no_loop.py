from copy import deepcopy

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    check_no_loop, sdk_ensure_upgrade_sent
from indy_node.server.upgrade_log import UpgradeLog
import indy_node


def test_upgrade_does_not_get_into_loop(looper, tconf, nodeSet,
                                        validUpgrade, sdk_pool_handle,
                                        sdk_wallet_trustee, monkeypatch):
    new_version = bumpedVersion()
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version

    # An upgrade scheduled, it should pass
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))

    # here we make nodes think they have upgraded successfully
    monkeypatch.setattr(indy_node.__metadata__, '__version__', new_version)
    check_no_loop(nodeSet, UpgradeLog.SUCCEEDED)
