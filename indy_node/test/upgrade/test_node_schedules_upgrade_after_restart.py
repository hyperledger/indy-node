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

from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled
from plenum.common.constants import VERSION
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from stp_core.loop.eventually import eventually


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
        node = testNodeClass(nm, basedirpath=tdirWithPoolTxns, base_data_dir=tdirWithPoolTxns,
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
