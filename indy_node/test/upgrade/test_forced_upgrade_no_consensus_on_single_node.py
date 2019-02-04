from indy_node.test import waits
from indy_node.test.upgrade.helper import bumpVersion, get_req_from_update
from plenum.common.constants import VERSION
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request
from stp_core.loop.eventually import eventually


def test_forced_upgrade_no_consensus_on_single_node(
        validUpgradeExpForceTrue, looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    nup = validUpgradeExpForceTrue.copy()
    nup.update({VERSION: bumpVersion(validUpgradeExpForceTrue[VERSION])})
    for node in nodeSet:
        if node.name != "Alpha" and node in looper.prodables:
            node.cleanupOnStopping = False
            looper.removeProdable(node)
            node.stop()
        else:
            node.upgrader.scheduledUpgrade = None
    _, did = sdk_wallet_trustee
    req = get_req_from_update(looper, did, nup)
    sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, req)

    def testsched():
        for node in nodeSet:
            if node.name == "Alpha":
                assert node.upgrader.scheduledAction
                assert node.upgrader.scheduledAction[0] == nup[VERSION]

    looper.run(eventually(testsched, retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
