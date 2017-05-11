from copy import deepcopy

from plenum.common.constants import VERSION
from plenum.test import waits as plenumWaits
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from sovrin_common.constants import CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from sovrin_node.test import waits
from sovrin_node.test.upgrade.helper import sendUpgrade, \
    checkUpgradeScheduled, checkNoUpgradeScheduled
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



def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, trustee,
                             trusteeWallet, validUpgrade):
    # here there is a dependency from 'testNodeSchedulesUpgradeAfterRestart'
    # we have to reconnect client after the nodes is restarted.
    looper.run(trustee.ensureConnectedToNodes())

    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    validUpgradeCopy[JUSTIFICATION] = '"not gonna give you one"'

    validUpgradeCopy.pop(SCHEDULE, None)
    upgrade, req = sendUpgrade(trustee, trusteeWallet, validUpgradeCopy)

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, retryWait=1, timeout=timeout))

    looper.run(eventually(checkNoUpgradeScheduled, nodeSet, retryWait=1,
                          timeout=waits.expectedNoUpgradeScheduled()))
