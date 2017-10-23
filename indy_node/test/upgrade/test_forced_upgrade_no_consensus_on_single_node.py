from indy_node.test import waits
from indy_node.test.upgrade.helper import sendUpgrade, bumpVersion
from plenum.common.constants import VERSION
from stp_core.loop.eventually import eventually


def test_forced_upgrade_no_consensus_on_single_node(
        validUpgradeExpForceTrue, looper, nodeSet, trustee, trusteeWallet):
    nup = validUpgradeExpForceTrue.copy()
    nup.update({VERSION: bumpVersion(validUpgradeExpForceTrue[VERSION])})
    for node in nodeSet:
        if node.name != "Alpha":
            node.cleanupOnStopping = False
            looper.removeProdable(node)
            node.stop()
        else:
            node.upgrader.scheduledUpgrade = None
    sendUpgrade(trustee, trusteeWallet, nup)

    def testsched():
        for node in nodeSet:
            if node.name == "Alpha":
                assert node.upgrader.scheduledUpgrade
                assert node.upgrader.scheduledUpgrade[0] == nup[VERSION]

    looper.run(eventually(testsched, retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
