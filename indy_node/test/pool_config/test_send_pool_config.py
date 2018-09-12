from indy_node.test.pool_config.helper import check_pool_config_writable_set, \
    sdk_ensure_pool_config_sent, sdk_pool_config_sent
from stp_core.loop.eventually import eventually

from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected


def test_send_pool_config_writes_false_force_false(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFF):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWFFF)
    check_pool_config_writable_set(nodeSet, False)


def test_send_pool_config_writes_true_force_true(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFT):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWTFT)
    check_pool_config_writable_set(nodeSet, True)


def test_send_pool_config_writes_false_force_true(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFT):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWFFT)
    check_pool_config_writable_set(nodeSet, False)


def test_send_pool_config_writes_true_force_false(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFF):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWTFF)
    check_pool_config_writable_set(nodeSet, True)


def test_send_pool_config_2_nodes_can_force_writes_false_force_true(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFT):
    assert len(nodeSet) == 4

    node1 = nodeSet[2]
    node0 = nodeSet[3]

    check_pool_config_writable_set(nodeSet, True)

    disconnect_node_and_ensure_disconnected(
        looper, nodeSet, node0.name, stopNode=False)
    disconnect_node_and_ensure_disconnected(
        looper, nodeSet, node1.name, stopNode=False)

    sdk_pool_config_sent(looper, sdk_pool_handle,
                         sdk_wallet_trustee, poolConfigWFFT)

    looper.run(eventually(check_pool_config_writable_set,
                          nodeSet[0:2], False, retryWait=1, timeout=10))
