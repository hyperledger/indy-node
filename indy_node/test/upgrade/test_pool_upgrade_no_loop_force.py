from copy import deepcopy

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from indy_common.constants import FORCE

from indy_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    check_no_loop, sdk_ensure_upgrade_sent, clear_aq_stash
from indy_node.server.upgrade_log import UpgradeLog
from indy_node.utils.node_control_utils import NodeControlUtil

whitelist = ['Failed to upgrade node']


def test_upgrade_does_not_get_into_loop_force(looper, tconf, nodeSet,
                                              validUpgrade, sdk_pool_handle,
                                              sdk_wallet_trustee, monkeypatch):
    new_version = bumpedVersion(validUpgrade['version'])
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version
    upgr1[FORCE] = True

    clear_aq_stash(nodeSet)

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
    monkeypatch.setattr(NodeControlUtil, '_get_curr_info',
                        lambda *x: "Version: {}".format(new_version))
    check_no_loop(nodeSet, UpgradeLog.Events.succeeded)
