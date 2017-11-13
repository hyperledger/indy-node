#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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
    looper.removeProdable(node0)
    disconnect_node_and_ensure_disconnected(
        looper, nodeSet, node1.name, stopNode=False)
    looper.removeProdable(node1)

    sendPoolConfig(trustee, trusteeWallet, poolConfigWFFT)

    looper.run(eventually(checkPoolConfigWritableSet,
                          nodeSet[0:2], False, retryWait=1, timeout=10))
