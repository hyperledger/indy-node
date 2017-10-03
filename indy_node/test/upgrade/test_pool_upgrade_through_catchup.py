import pytest
from copy import deepcopy

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION, NAME
from plenum.common.util import randomString
from plenum.test.test_node import checkNodesConnected
from indy_common.constants import SHA256, CANCEL, ACTION
from indy_common.test.conftest import tconf
from indy_client.test.conftest import testNodeClass
from indy_client.test.conftest import testClientClass
from plenum.test.conftest import allPluginsPath
from indy_node.test.helper import TestNode
from indy_node.test.upgrade.helper import bumpVersion, sendUpgrade, \
    ensureUpgradeSent, checkUpgradeScheduled, get_valid_code_hash
from plenum.test import waits as plenumWaits

whitelist = ['Failed to upgrade node']


@pytest.fixture(scope="module")
def txnPoolNodeSet(tconf, nodeSet):
    for node in nodeSet:
        node.config = tconf
        node.upgrader.config = tconf
    return nodeSet


@pytest.mark.skip(reason='SOV-559')
def testUpgradeLatestUncancelledVersion(looper,
                                        txnPoolNodeSet, tconf, nodeThetaAdded,
                                        validUpgrade, trustee, trusteeWallet,
                                        tdirWithPoolTxns, allPluginsPath):
    """
    A node starts and finds several upgrades but selects the latest one which
    is not cancelled, eg node is on version 1.2 but finds 1.3, 1.4 and 1.5 but
    since 1.5 is cancelled, it selects 1.4
    """
    nodeSet = txnPoolNodeSet
    newSteward, newStewardWallet, newNode = nodeThetaAdded
    for node in nodeSet[:-1]:
        node.nodestack.removeRemoteByName(newNode.nodestack.name)
        newNode.nodestack.removeRemoteByName(node.nodestack.name)
    newNode.stop()
    nodeSet = nodeSet[:-1]
    looper.removeProdable(newNode)

    upgr1 = deepcopy(validUpgrade)

    upgr2 = deepcopy(upgr1)
    upgr2[VERSION] = bumpVersion(upgr1[VERSION])
    upgr2[NAME] += randomString(3)
    # upgr2[SHA256] = get_valid_code_hash()
    upgr2[SHA256] = 'db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55'

    upgr3 = deepcopy(upgr2)
    upgr3[VERSION] = bumpVersion(upgr2[VERSION])
    upgr3[NAME] += randomString(3)
    # upgr3[SHA256] = get_valid_code_hash()
    upgr3[SHA256] = '112c060527e8cecfafe64dcb5bdabc4010cc7b64e0bf9bc2a43d23c37d927128'

    upgr4 = deepcopy(upgr3)
    upgr4[ACTION] = CANCEL

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(eventually(checkUpgradeScheduled,
                          nodeSet[:-1],
                          upgr1[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr2)
    looper.run(eventually(checkUpgradeScheduled,
                          nodeSet[:-1],
                          upgr2[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr3)
    looper.run(eventually(checkUpgradeScheduled,
                          nodeSet[:-1],
                          upgr3[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))

    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr4)
    looper.run(eventually(checkUpgradeScheduled,
                          nodeSet[:-1],
                          upgr2[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))

    trustee.stopRetrying()

    newNode = TestNode(newNode.name, basedirpath=tdirWithPoolTxns, base_data_dir=tdirWithPoolTxns,
                       config=tconf, pluginPaths=allPluginsPath,
                       ha=newNode.nodestack.ha, cliha=newNode.clientstack.ha)
    looper.add(newNode)
    nodeSet.append(newNode)
    looper.run(checkNodesConnected(nodeSet))

    looper.run(eventually(checkUpgradeScheduled, [newNode, ], upgr2[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))
