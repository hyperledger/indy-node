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

from plenum.test import waits as plenumWaits
from indy_common.constants import CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from indy_node.test import waits
from indy_node.test.upgrade.helper import sendUpgrade, \
    checkNoUpgradeScheduled
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node']


def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, trustee,
                             trusteeWallet, validUpgrade):
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
