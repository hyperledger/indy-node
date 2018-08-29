from plenum.test.node_catchup.helper import waitNodeDataEquality
from indy_node.test.conftest import sdk_node_theta_added
from indy_node.test.helper import TestNode
from indy_common.config_helper import NodeConfigHelper
from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_requests_post_multiple_new_nodes(
        looper,
        nodeSet,
        tconf,
        tdir,
        sdk_pool_handle,
        sdk_wallet_trustee,
        allPluginsPath,
        some_transactions_done):
    new_nodes = []
    for node_name in ('Zeta', 'Eta'):
        new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                            nodeSet,
                                                            tdir,
                                                            tconf,
                                                            sdk_pool_handle,
                                                            sdk_wallet_trustee,
                                                            allPluginsPath,
                                                            node_config_helper_class=NodeConfigHelper,
                                                            testNodeClass=TestNode,
                                                            name=node_name)
        new_nodes.append(new_node)

    for _ in range(5):
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)

    for new_node in new_nodes:
        waitNodeDataEquality(looper, new_node, *nodeSet[:-2])

    for _ in range(5):
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
