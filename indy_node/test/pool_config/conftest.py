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

from plenum.common.constants import STEWARD

from indy_common.constants import START, FORCE
from indy_node.test import waits
from indy_node.test.pool_config.helper import ensurePoolConfigSent
from indy_client.test.helper import getClientAddedWithRole
from stp_core.loop.eventually import eventually


def genPoolConfig(writes: bool, force: bool):
    return dict(writes=writes, force=force)


@pytest.fixture(scope='module')
def poolConfigWTFF():
    return genPoolConfig(writes=True, force=False)


@pytest.fixture(scope='module')
def poolConfigWFFF():
    return genPoolConfig(writes=False, force=False)


@pytest.fixture(scope='module')
def poolConfigWTFT():
    return genPoolConfig(writes=True, force=True)


@pytest.fixture(scope='module')
def poolConfigWFFT():
    return genPoolConfig(writes=False, force=True)


@pytest.fixture(scope="module")
def poolConfigSent(looper, nodeSet, trustee, trusteeWallet, poolCfg):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolCfg)
