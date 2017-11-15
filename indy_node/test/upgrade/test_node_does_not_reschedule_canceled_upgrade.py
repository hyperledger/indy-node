#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from copy import deepcopy

from indy_common.constants import ACTION, CANCEL, SCHEDULE
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkNoUpgradeScheduled, \
    ensureUpgradeSent
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from stp_core.loop.eventually import eventually


def test_node_does_not_reschedule_cancelled_upgrade_after_restart(
        upgradeScheduled, looper, nodeSet, validUpgrade,
        testNodeClass, tdirWithPoolTxns, tconf, allPluginsPath,
        trustee, trusteeWallet):

    # Cancel the scheduled upgrade
    valid_upgrade_cancel = deepcopy(validUpgrade)
    valid_upgrade_cancel[ACTION] = CANCEL
    del valid_upgrade_cancel[SCHEDULE]

    ensureUpgradeSent(looper, trustee, trusteeWallet, valid_upgrade_cancel)

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
        node = testNodeClass(nm, basedirpath=tdirWithPoolTxns,
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
