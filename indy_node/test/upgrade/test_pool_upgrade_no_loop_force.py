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
from indy_common.constants import FORCE

from indy_node.test.upgrade.helper import bumpedVersion, checkUpgradeScheduled, \
    ensureUpgradeSent, check_no_loop
from indy_node.server.upgrade_log import UpgradeLog
import indy_node

whitelist = ['Failed to upgrade node']


def test_upgrade_does_not_get_into_loop_force(looper, tconf, nodeSet,
                                              validUpgrade, trustee,
                                              trusteeWallet, monkeypatch):
    new_version = bumpedVersion()
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = new_version
    upgr1[FORCE] = True

    # An upgrade scheduled, it should pass
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))

    # here we make nodes think they have upgraded successfully
    monkeypatch.setattr(indy_node.__metadata__, '__version__', new_version)
    check_no_loop(nodeSet, UpgradeLog.UPGRADE_SUCCEEDED)
