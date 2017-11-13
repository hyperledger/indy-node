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

import dateutil
from datetime import timedelta

from indy_common.constants import SCHEDULE
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled, \
    ensureUpgradeSent
from plenum.common.constants import VERSION
from stp_core.loop.eventually import eventually


def test_node_schedules_upgrade_for_proper_datetime(
        looper, tconf, nodeSet, validUpgrade, trustee, trusteeWallet):

    upgr1 = deepcopy(validUpgrade)
    # Upgrade of each node will be scheduled for its own day
    # (since today with one day step)
    deltaDays = 0
    for nodeId in upgr1[SCHEDULE]:
        nodeUpgradeDateTime = dateutil.parser.parse(upgr1[SCHEDULE][nodeId])
        nodeUpgradeDateTime += timedelta(days=deltaDays)
        upgr1[SCHEDULE][nodeId] = nodeUpgradeDateTime.isoformat()
        deltaDays += 1

    # Upgrade is scheduled for the proper datetime for each node
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            upgr1[SCHEDULE],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
