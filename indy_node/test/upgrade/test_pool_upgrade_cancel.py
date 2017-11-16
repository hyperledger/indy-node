from copy import deepcopy

from plenum.test import waits as plenumWaits
from indy_common.constants import CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from indy_node.test import waits
from indy_node.test.upgrade.helper import sendUpgrade, \
    checkNoUpgradeScheduled
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node']


def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, trustee,
                             trusteeWallet, validUpgrade):
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    validUpgradeCopy[JUSTIFICATION] = '"not gonna give you one"'

    validUpgradeCopy.pop(SCHEDULE, None)
    upgrade, req = sendUpgrade(trustee, trusteeWallet, validUpgradeCopy)

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, retryWait=1, timeout=timeout))

    looper.run(eventually(checkNoUpgradeScheduled, nodeSet, retryWait=1,
                          timeout=waits.expectedNoUpgradeScheduled()))
