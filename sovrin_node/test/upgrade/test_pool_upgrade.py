from plenum.common.constants import VERSION
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from sovrin_node.test import waits
from sovrin_node.test.upgrade.helper import checkUpgradeScheduled, sendUpgrade, bumpVersion
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node']


def testNodeSchedulesUpgrade(upgradeScheduled):
    pass


def testNodeSchedulesUpgradeAfterRestart(upgradeScheduled, looper, nodeSet,
                                         validUpgrade, testNodeClass,
                                         tdirWithPoolTxns, tconf,
                                         allPluginsPath):
    names = []
    while nodeSet:
        node = nodeSet.pop()
        names.append(node.name)
        node.cleanupOnStopping = False
        looper.removeProdable(node)
        node.stop()
        del node

    for nm in names:
        node = testNodeClass(nm, basedirpath=tdirWithPoolTxns,
                             config=tconf, pluginPaths=allPluginsPath)
        looper.add(node)
        nodeSet.append(node)

    looper.run(checkNodesConnected(nodeSet))
    ensureElectionsDone(looper=looper, nodes=nodeSet, retryWait=1)
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))


def testNodeSchedulesUpgradeExpForceFalse(upgradeScheduledExpForceFalse):
    pass


def testNodeSchedulesUpgradeExpForceTrue(upgradeScheduledExpForceTrue):
    pass


def testForcedUpgradeNoConsensusOnSingleNode(validUpgradeExpForceTrue, looper, nodeSet, trustee, trusteeWallet):
    nup = validUpgradeExpForceTrue.copy()
    nup.update({VERSION: bumpVersion(validUpgradeExpForceTrue[VERSION])})
    for node in nodeSet:
        if node.name != "Alpha":
            node.cleanupOnStopping = False
            looper.removeProdable(node)
            node.stop()
        else:
            node.upgrader.scheduledUpgrade = None
    sendUpgrade(trustee, trusteeWallet, nup)

    def testsched():
        for node in nodeSet:
            if node.name == "Alpha":
                assert node.upgrader.scheduledUpgrade
                assert node.upgrader.scheduledUpgrade[0] == nup[VERSION]

    looper.run(eventually(testsched, retryWait=1, timeout=waits.expectedUpgradeScheduled()))