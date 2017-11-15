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
from indy_node.test.upgrade.helper import sendUpgrade, bumpVersion
from plenum.common.constants import VERSION
from stp_core.loop.eventually import eventually


def test_forced_upgrade_no_consensus_on_single_node(
        validUpgradeExpForceTrue, looper, nodeSet, trustee, trusteeWallet):
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

    looper.run(eventually(testsched, retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
