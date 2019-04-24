from indy_node.server.upgrade_log import UpgradeLog
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled, \
    sdk_ensure_upgrade_sent, count_action_log_package
from plenum.common.constants import VERSION
from plenum.test.delayers import req_delay
from plenum.test.test_node import getNonPrimaryReplicas
from stp_core.loop.eventually import eventually


def test_forced_upgrade_handled_once_if_ordered_and_then_request_received(
        looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee,
        validUpgradeExpForceTrue):
    """
    Verifies that POOL_UPGRADE force=true request is handled one time in case
    the node commits the transaction to the ledger and only after that receives
    the request directly from the client
    """
    slow_node = getNonPrimaryReplicas(nodeSet, instId=0)[-1].node
    slow_node.clientIbStasher.delay(req_delay())

    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                            validUpgradeExpForceTrue)

    looper.run(eventually(checkUpgradeScheduled,
                          [slow_node],
                          validUpgradeExpForceTrue[VERSION],
                          retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))

    slow_node.clientIbStasher.reset_delays_and_process_delayeds()
    looper.runFor(waits.expectedUpgradeScheduled())

    checkUpgradeScheduled([slow_node], validUpgradeExpForceTrue[VERSION])
    assert count_action_log_package(list(slow_node.upgrader._actionLog), validUpgradeExpForceTrue['package']) == 1
    assert slow_node.upgrader._actionLog.last_event.ev_type == UpgradeLog.Events.scheduled
