from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled, \
    sdk_send_upgrade
from plenum.common.constants import VERSION
from plenum.test.delayers import req_delay, ppDelay, pDelay, cDelay, ppgDelay
from plenum.test.test_node import getNonPrimaryReplicas
from stp_core.loop.eventually import eventually


def test_node_handles_forced_upgrade_on_propagate(
        looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee,
        validUpgradeExpForceTrue):
    """
    Verifies that POOL_UPGRADE force=true request is handled immediately when
    the node receives it in a PROPAGATE from any other node
    """
    slow_node = getNonPrimaryReplicas(nodeSet, instId=0)[-1].node

    # Stash all except PROPAGATEs from Gamma
    slow_node.clientIbStasher.delay(req_delay())
    slow_node.nodeIbStasher.delay(ppgDelay(sender_filter='Alpha'))
    slow_node.nodeIbStasher.delay(ppgDelay(sender_filter='Beta'))
    slow_node.nodeIbStasher.delay(ppDelay())
    slow_node.nodeIbStasher.delay(pDelay())
    slow_node.nodeIbStasher.delay(cDelay())

    sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee,
                     validUpgradeExpForceTrue)

    looper.run(eventually(checkUpgradeScheduled,
                          [slow_node],
                          validUpgradeExpForceTrue[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))
