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

import dateutil
import pytest
from datetime import timedelta, datetime

from indy_client.test.cli.test_pool_upgrade import poolUpgradeSubmitted
from indy_client.test.cli.test_pool_upgrade import poolUpgradeScheduled
from indy_node.test.upgrade.conftest import validUpgrade as _validUpgrade


@pytest.fixture(scope='module')
def validUpgrade(_validUpgrade):
    # Add 5 days to the time of the upgrade of each node in schedule parameter
    # of send POOL_UPGRADE command
    upgradeSchedule = _validUpgrade['schedule']
    for nodeId in upgradeSchedule:
        nodeUpgradeDateTime = dateutil.parser.parse(upgradeSchedule[nodeId])
        nodeUpgradeDateTime += timedelta(days=5)
        upgradeSchedule[nodeId] = nodeUpgradeDateTime.isoformat()
    return _validUpgrade


def test_node_upgrade_scheduled_on_proper_date(poolNodesStarted,
                                               poolUpgradeScheduled):
    # Verify that the upgrade is scheduled in approximately 5 days for each node
    now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    for node in poolNodesStarted.nodes.values():
        assert (node.upgrader.scheduledUpgrade[1] - now).days == 5
