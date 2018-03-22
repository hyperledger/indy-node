import pytest
from indy_node.test.pool_config.helper import ensurePoolConfigSent, checkPoolConfigWritableSet, sendPoolConfig
from stp_core.loop.eventually import eventually

from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected


def test_send_pool_config_writes_false_force_false(
        nodeSet, looper, trustee, trusteeWallet, poolConfigWFFF):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolConfigWFFF)
    checkPoolConfigWritableSet(nodeSet, False)


def test_send_pool_config_writes_true_force_true(
        nodeSet, looper, trustee, trusteeWallet, poolConfigWTFT):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolConfigWTFT)
    checkPoolConfigWritableSet(nodeSet, True)


def test_send_pool_config_writes_false_force_true(
        nodeSet, looper, trustee, trusteeWallet, poolConfigWFFT):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolConfigWFFT)
    checkPoolConfigWritableSet(nodeSet, False)


def test_send_pool_config_writes_true_force_false(
        nodeSet, looper, trustee, trusteeWallet, poolConfigWTFF):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolConfigWTFF)
    checkPoolConfigWritableSet(nodeSet, True)


def test_send_pool_config_2_nodes_can_force_writes_false_force_true(
        nodeSet, looper, trustee, trusteeWallet, poolConfigWFFT):
    assert len(nodeSet) == 4

    node1 = nodeSet[2]
    node0 = nodeSet[3]

    checkPoolConfigWritableSet(nodeSet, True)

    disconnect_node_and_ensure_disconnected(
        looper, nodeSet, node0.name, stopNode=False)
    disconnect_node_and_ensure_disconnected(
        looper, nodeSet, node1.name, stopNode=False)

    sendPoolConfig(trustee, trusteeWallet, poolConfigWFFT)

    looper.run(eventually(checkPoolConfigWritableSet,
                          nodeSet[0:2], False, retryWait=1, timeout=10))
