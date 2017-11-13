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

import pytest

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import codeVersion, checkUpgradeScheduled, \
    ensureUpgradeSent


def test_do_not_upgrade_to_the_same_version(looper, tconf, nodeSet,
                                            validUpgrade, trustee,
                                            trusteeWallet):
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = codeVersion()

    # An upgrade is not scheduled
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    with pytest.raises(AssertionError):
        looper.run(
            eventually(
                checkUpgradeScheduled,
                nodeSet,
                upgr1[VERSION],
                retryWait=1,
                timeout=waits.expectedUpgradeScheduled()))
