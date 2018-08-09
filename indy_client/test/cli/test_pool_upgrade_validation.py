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
              "InvalidClientRequest('Version is not upgradable'"

    be(trusteeCli)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} package={package}',
       mapper=upgrade, expect=['Sending pool upgrade', err_msg], within=10)


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsEmpty(
        be, do, validUpgrade, trusteeCli):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = ''

    be(trusteeCli)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} justification={justification} package={package}',
       mapper=upgrade, expect=INVALID_SYNTAX, within=10)


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsVeryLong(
        be, do, validUpgrade, trusteeCli):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = randomString(JUSTIFICATION_MAX_SIZE + 1)

    be(trusteeCli)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} justification={justification}',
       mapper=upgrade, expect=INVALID_SYNTAX, within=10)
