from plenum.test.test_node import ensure_node_disconnected, getNonPrimaryReplicas
from indy_node.test.helper import addRawAttribute


from indy_client.test.conftest import nodeSet
from indy_common.test.conftest import config_helper_class, node_config_helper_class


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
