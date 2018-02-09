from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled
from plenum.common.constants import VERSION
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from stp_core.loop.eventually import eventually
from indy_common.config_helper import NodeConfigHelper


def testNodeSchedulesUpgradeAfterRestart(upgradeScheduled, looper, nodeSet,
                                         validUpgrade, testNodeClass,
                                         tdir, tconf, allPluginsPath):
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
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            validUpgrade[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
