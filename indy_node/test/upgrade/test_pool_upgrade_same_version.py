from copy import deepcopy

import pytest

from plenum.common.exceptions import RequestRejectedException
from plenum.common.constants import VERSION

from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent, lowerVersion


def test_do_not_upgrade_to_the_same_version(looper, tconf, nodeSet,
                                            validUpgrade, sdk_pool_handle,
                                            sdk_wallet_trustee):
    upgr1 = deepcopy(validUpgrade)
    upgr1[VERSION] = lowerVersion(validUpgrade['version'])

    # An upgrade is not scheduled
    with pytest.raises(RequestRejectedException) as ex:
        sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgr1)
    ex.match("Version {} is not upgradable".format(upgr1[VERSION]))
