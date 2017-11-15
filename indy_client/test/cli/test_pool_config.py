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

from indy_node.test.upgrade.conftest import validUpgrade
from indy_client.test.cli.constants import INVALID_SYNTAX
from plenum.common.constants import VERSION


def testPoolConfigInvalidSyntax(be, do, trusteeCli):
    be(trusteeCli)
    do('send POOL_CONFIG wites=True force=False', expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=Tue force=False', expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=True froce=False',
       expect=INVALID_SYNTAX, within=10)
    do('send POOL_CONFIG writes=True force=1', expect=INVALID_SYNTAX, within=10)


def testPoolConfigWritableFalse(be, do, trusteeCli):
    be(trusteeCli)
    do('send POOL_CONFIG writes=False force=False',
       expect="Pool config successful", within=10)
    do('send NYM dest=33333333333333333333333333333333333333333333',
       expect="Pool is in readonly mode", within=10)


def testPoolConfigWritableTrue(be, do, trusteeCli):
    be(trusteeCli)
    do('send NYM dest=33333333333333333333333333333333333333333333',
       expect="Pool is in readonly mode", within=10)
    do('send POOL_CONFIG writes=True force=False',
       expect="Pool config successful", within=10)
    do('send NYM dest=33333333333333333333333333333333333333333333',
       expect="added", within=10)


def testPoolConfigWritableFalseCanRead(be, do, trusteeCli):
    be(trusteeCli)
    do('send NYM dest=44444444444444444444444444444444444444444444',
       expect="added", within=10)
    do('send GET_NYM dest=44444444444444444444444444444444444444444444',
       expect="Current verkey is same as DID", within=10)
    do('send POOL_CONFIG writes=False force=False',
       expect="Pool config successful", within=10)
    do('send NYM dest=55555555555555555555555555555555555555555555',
       expect="Pool is in readonly mode", within=10)
    do('send GET_NYM dest=44444444444444444444444444444444444444444444',
       expect="Current verkey is same as DID", within=10)


def testPoolUpgradeOnReadonlyPool(
        poolNodesStarted, be, do, trusteeCli, validUpgrade):
    be(trusteeCli)
    do('send POOL_CONFIG writes=False force=False',
       expect="Pool config successful", within=10)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} action={action} schedule={schedule} timeout={timeout}',
       within=10, expect=['Sending pool upgrade', 'Pool Upgrade Transaction Scheduled'], mapper=validUpgrade)

    for node in poolNodesStarted.nodes.values():
        assert len(node.upgrader.aqStash) > 0
        assert node.upgrader.scheduledUpgrade
        assert node.upgrader.scheduledUpgrade[0] == validUpgrade[VERSION]
