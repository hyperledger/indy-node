from copy import deepcopy

from indy_common.constants import ACTION, CANCEL, SCHEDULE
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkNoUpgradeScheduled, \
    sdk_ensure_upgrade_sent
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from stp_core.loop.eventually import eventually
from indy_common.config_helper import NodeConfigHelper


def test_node_does_not_reschedule_cancelled_upgrade_after_restart(
        upgradeScheduled, looper, nodeSet, validUpgrade,
        testNodeClass, tdir, tconf, allPluginsPath,
        sdk_pool_handle, sdk_wallet_trustee):
    # Cancel the scheduled upgrade
    valid_upgrade_cancel = deepcopy(validUpgrade)
    valid_upgrade_cancel[ACTION] = CANCEL
    del valid_upgrade_cancel[SCHEDULE]

    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, valid_upgrade_cancel)

    # Verify that no upgrade is scheduled now
    looper.run(
        eventually(
            checkNoUpgradeScheduled,
            nodeSet,
            retryWait=1,
            timeout=waits.expectedNoUpgradeScheduled()))

    # Restart all the nodes
    names = []
    while nodeSet:
        node = nodeSet.pop()
        names.append(node.name)
        node.cleanupOnStopping = False
        looper.removeProdable(node)
        node.stop()
        del node

    for nm in names:
        config_helper = NodeConfigHelper(nm, tconf, chroot=tdir)
        node = testNodeClass(nm, config_helper=config_helper,
                             config=tconf, pluginPaths=allPluginsPath)
        looper.add(node)
        nodeSet.append(node)

    looper.run(checkNodesConnected(nodeSet))
    ensureElectionsDone(looper=looper, nodes=nodeSet, retryWait=1)

    # Verify that still no upgrade is scheduled
    looper.run(
        eventually(
            checkNoUpgradeScheduled,
            nodeSet,
            retryWait=1,
            timeout=waits.expectedNoUpgradeScheduled()))
