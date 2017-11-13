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

from indy_node.test.upgrade.conftest import validUpgrade
from indy_client.test.cli.constants import INVALID_SYNTAX, ERROR
from indy_node.test.upgrade.helper import loweredVersion
from plenum.common.constants import VERSION
from plenum.common.util import randomString
from indy_common.constants import JUSTIFICATION, JUSTIFICATION_MAX_SIZE


def testPoolUpgradeFailsIfVersionIsLowerThanCurrent(
        be, do, validUpgrade, trusteeCli):
    upgrade = deepcopy(validUpgrade)
    upgrade[VERSION] = loweredVersion()

    err_msg = "Pool upgrade failed: client request invalid: " \
              "InvalidClientRequest('Upgrade to lower version is not allowed'"

    be(trusteeCli)
    do(
        'send POOL_UPGRADE name={name} version={version} sha256={sha256} '
        'action={action} schedule={schedule} timeout={timeout}',
        mapper=upgrade,
        expect=['Sending pool upgrade', err_msg],
        within=10)


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsEmpty(
        be, do, validUpgrade, trusteeCli):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = ''

    be(trusteeCli)
    do(
        'send POOL_UPGRADE name={name} version={version} sha256={sha256} '
        'action={action} schedule={schedule} timeout={timeout} justification={justification}',
        mapper=upgrade,
        expect=INVALID_SYNTAX,
        within=10)


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsVeryLong(
        be, do, validUpgrade, trusteeCli):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = randomString(JUSTIFICATION_MAX_SIZE + 1)

    be(trusteeCli)
    do(
        'send POOL_UPGRADE name={name} version={version} sha256={sha256} '
        'action={action} schedule={schedule} timeout={timeout} justification={justification}',
        mapper=upgrade,
        expect=INVALID_SYNTAX,
        within=10)
