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

import pytest

import indy_node
from stp_core.loop.eventually import eventually
from indy_common.constants import IN_PROGRESS, COMPLETE
from indy_node.test.upgrade.helper import populate_log_with_upgrade_events, check_node_set_acknowledges_upgrade
from plenum.test import waits as plenumWaits


whitelist = ['unable to send message']
# TODO: Implement a client in node


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tconf):
    # For each node, adding a file with he current version number which makes the node
    # think that an upgrade has been performed
    populate_log_with_upgrade_events(
        tdirWithPoolTxns,
        poolTxnNodeNames,
        tconf,
        indy_node.__metadata__.__version__)
    return tdirWithPoolTxns


def testNodeDetectsUpgradeDone(looper, nodeSet):
    def check():
        for node in nodeSet:
            assert node.upgrader.lastUpgradeEventInfo[2] == indy_node.__metadata__.__version__

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, retryWait=1, timeout=timeout))


def testSendNodeUpgradeToAllNodes(looper, nodeSet, nodeIds):
    check_node_set_acknowledges_upgrade(
        looper, nodeSet, nodeIds, [
            IN_PROGRESS, COMPLETE], indy_node.__metadata__.__version__)
