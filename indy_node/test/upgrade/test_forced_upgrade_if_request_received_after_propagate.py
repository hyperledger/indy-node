from indy_node.server.upgrade_log import UpgradeLog
from indy_node.test import waits
from indy_node.test.upgrade.helper import checkUpgradeScheduled, sdk_ensure_upgrade_sent
from plenum.common.constants import VERSION
from plenum.common.messages.node_messages import Propagate
from plenum.common.request import Request
from plenum.test.delayers import req_delay, ppgDelay
from plenum.test.test_node import getNonPrimaryReplicas


def test_forced_upgrade_handled_once_if_request_received_after_propagate(
        looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee,
        validUpgradeExpForceTrue):
    """
    Verifies that POOL_UPGRADE force=true request is handled one time in case
    the node commits the transaction to the ledger but during the 3PC-process
    receives the request directly from the client after a PROPAGATE from some
    other node
    """
    slow_node = getNonPrimaryReplicas(nodeSet, instId=0)[-1].node

    slow_node.clientIbStasher.delay(req_delay())
    slow_node.nodeIbStasher.delay(ppgDelay(sender_filter='Beta'))
    slow_node.nodeIbStasher.delay(ppgDelay(sender_filter='Gamma'))

    original_process_propagate = slow_node.nodeMsgRouter.routes[Propagate]
    original_process_request = slow_node.clientMsgRouter.routes[Request]

    def patched_process_propagate(msg: Propagate, frm: str):
        original_process_propagate(msg, frm)
        slow_node.clientIbStasher.reset_delays_and_process_delayeds()
        slow_node.nodeMsgRouter.routes[Propagate] = original_process_propagate

    def patched_process_request(request: Request, frm: str):
        original_process_request(request, frm)
        slow_node.nodeIbStasher.reset_delays_and_process_delayeds()
        slow_node.clientMsgRouter.routes[Request] = original_process_request

    slow_node.nodeMsgRouter.routes[Propagate] = patched_process_propagate
    slow_node.clientMsgRouter.routes[Request] = patched_process_request

    init_len = len(list(slow_node.upgrader._actionLog))

    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                            validUpgradeExpForceTrue)

    looper.runFor(waits.expectedUpgradeScheduled())

    checkUpgradeScheduled([slow_node], validUpgradeExpForceTrue[VERSION])
    if init_len ==0:
        # first upgrade - should be only one scheduled
        assert len(list(slow_node.upgrader._actionLog)) == 1
    else:
        # one upgrade were already scheduled. we should cancel it and schedule new one
        # so action log should be increased by 2
        assert len(list(slow_node.upgrader._actionLog)) == init_len + 2
    assert slow_node.upgrader._actionLog.lastEvent[1] == UpgradeLog.SCHEDULED
