from copy import deepcopy
import pytest

from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.common.constants import VERSION
from plenum.common.util import randomString
from indy_node.test.upgrade.helper import loweredVersion, sdk_ensure_upgrade_sent
from indy_common.constants import JUSTIFICATION, JUSTIFICATION_MAX_SIZE

from indy_node.test.upgrade.conftest import validUpgrade, nodeIds


def testPoolUpgradeFailsIfVersionIsLowerThanCurrent(
        looper, sdk_pool_handle, validUpgrade, sdk_wallet_trustee):
    upgrade = deepcopy(validUpgrade)
    upgrade[VERSION] = loweredVersion()

    with pytest.raises(RequestRejectedException) as e:
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgrade)
    e.match('Version is not upgradable')


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsEmpty(
        looper, sdk_pool_handle, validUpgrade, sdk_wallet_trustee):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = ''

    with pytest.raises(RequestNackedException) as e:
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgrade)
    e.match('empty string')


def testPoolUpgradeHasInvalidSyntaxIfJustificationIsVeryLong(
        looper, sdk_pool_handle, validUpgrade, sdk_wallet_trustee):
    upgrade = deepcopy(validUpgrade)
    upgrade[JUSTIFICATION] = randomString(JUSTIFICATION_MAX_SIZE + 1)

    with pytest.raises(RequestNackedException) as e:
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgrade)
    e.match('is longer than {} symbols'.format(JUSTIFICATION_MAX_SIZE))
