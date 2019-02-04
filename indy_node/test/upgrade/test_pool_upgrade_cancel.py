from copy import deepcopy

from indy_common.constants import CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkNoUpgradeScheduled, sdk_send_upgrade
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node']


def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, sdk_pool_handle,
                             sdk_wallet_trustee, validUpgrade):
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    validUpgradeCopy[JUSTIFICATION] = '"never gonna give you one"'

    validUpgradeCopy.pop(SCHEDULE, None)
    sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee, validUpgradeCopy)

    looper.run(eventually(checkNoUpgradeScheduled, nodeSet, retryWait=1,
                          timeout=waits.expectedNoUpgradeScheduled()))
