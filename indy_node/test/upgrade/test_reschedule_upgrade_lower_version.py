from copy import deepcopy

from indy_common.constants import SHA256
from indy_node.test import waits
from indy_node.test.upgrade.helper import bumpVersion, checkUpgradeScheduled, \
    ensureUpgradeSent
from plenum.common.constants import VERSION, NAME
from plenum.common.util import randomString
from stp_core.loop.eventually import eventually


def testRescheduleUpgradeToLowerVersionThanPreviouslyScheduled(
        looper, tconf, nodeSet, validUpgrade, trustee, trusteeWallet):
    """
    A node starts at version 1.2 running has scheduled upgrade for version 1.5
    but get a txn for upgrade 1.4, it will schedule it and cancel upgrade to 1.5.
    """
    upgr1 = deepcopy(validUpgrade)

    upgr2 = deepcopy(upgr1)
    upgr2[VERSION] = bumpVersion(upgr1[VERSION])
    upgr2[NAME] += randomString(3)
    # upgr2[SHA256] = get_valid_code_hash()
    upgr2[SHA256] = 'ef9c3984e7a31994d4f692139116120bd0dd1ff7e270b6a2d773f8f2f9214d4c'

    # An upgrade for higher version scheduled, it should pass
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr2)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr2[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))

    # An upgrade for lower version scheduled, the transaction should pass and
    # the upgrade should be scheduled
    ensureUpgradeSent(looper, trustee, trusteeWallet, upgr1)
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            upgr1[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))
