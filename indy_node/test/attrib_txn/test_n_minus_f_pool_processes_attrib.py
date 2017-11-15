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

from plenum.test.test_node import ensure_node_disconnected, getNonPrimaryReplicas
from indy_node.test.helper import addRawAttribute


def test_n_minus_f_pool_processes_attrib(looper, nodeSet, up,
                                         steward, stewardWallet):
    """
    The pool N-f nodes should be able to process ATTRIB txn.
    https://jira.hyperledger.org/browse/INDY-245
    """
    make_pool_n_minus_f_nodes(looper, nodeSet)

    addRawAttribute(looper, steward, stewardWallet,
                    'foo', 'bar')


def make_pool_n_minus_f_nodes(looper, nodeSet):
    non_primary, other_nodes = get_any_non_primary_and_others(nodeSet)
    disconnect_node(looper, non_primary, other_nodes)


def get_any_non_primary_and_others(node_set):
    non_primary_node = getNonPrimaryReplicas(node_set, 0)[0].node
    other_nodes = [n for n in node_set if n != non_primary_node]
    return non_primary_node, other_nodes


def disconnect_node(looper, node, other_nodes):
    node.stop()
    looper.removeProdable(node)
    ensure_node_disconnected(looper, node, other_nodes)
    check_if_pool_n_minus_f(other_nodes)


def check_if_pool_n_minus_f(nodes):
    for node in nodes:
        min_connection = node.minimumNodes - 1  # subtract node itself
        assert len(node.nodestack.connecteds) == min_connection, \
            "the pool should have minimum (N-f) nodes connected"
