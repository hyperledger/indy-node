from copy import deepcopy

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from indy_common.constants import REINSTALL

from indy_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    check_no_loop, sdk_ensure_upgrade_sent
from indy_node.server.upgrade_log import UpgradeLog

whitelist = ['Failed to upgrade node',
             'failed upgrade',
             'This problem may have external reasons, check syslog for more information']


def test_upgrade_does_not_get_into_loop_if_reinstall_and_failed(
        looper, tconf, nodeSet, validUpgrade, sdk_pool_handle, sdk_wallet_trustee, monkeypatch):
    new_version = bumpedVersion()
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version
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

    # we have not patched indy_node version so nodes think the upgrade had
    # failed
    check_no_loop(nodeSet, UpgradeLog.FAILED)
