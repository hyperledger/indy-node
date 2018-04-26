from plenum.common.util import randomString
from plenum.test.node_catchup.helper import waitNodeDataEquality
from indy_client.test.client import TestClient
from indy_client.test.helper import getClientAddedWithRole
from indy_node.test.conftest import nodeThetaAdded
from indy_node.test.helper import TestNode
from indy_common.config_helper import NodeConfigHelper


def test_requests_post_multiple_new_nodes(
        looper,
        tdirWithClientPoolTxns,
        tdirWithDomainTxnsUpdated,
        nodeSet,
        tconf,
        tdir,
        trustee,
        trusteeWallet,
        allPluginsPath,
        some_transactions_done):
    new_nodes = []
    for node_name in ('Zeta', 'Eta'):
        new_steward, new_steward_wallet, new_node = nodeThetaAdded(looper,
                                                                   nodeSet,
                                                                   tdirWithClientPoolTxns,
                                                                   tconf,
                                                                   trustee,
                                                                   trusteeWallet,
                                                                   allPluginsPath,
                                                                   TestNode,
                                                                   TestClient,
                                                                   NodeConfigHelper,
                                                                   tdir,
                                                                   node_name=node_name)
        new_nodes.append((new_steward, new_steward_wallet, new_node))

    for _ in range(5):
        getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper, trustee,
                               trusteeWallet, randomString(6))

    for (_, _, new_node) in new_nodes:
        waitNodeDataEquality(looper, new_node, *nodeSet[:-2])

    for _ in range(5):
        getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper, trustee,
                               trusteeWallet, randomString(6))
