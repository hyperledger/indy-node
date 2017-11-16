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

from plenum.common.util import randomString
from plenum.test.node_catchup.helper import waitNodeDataEquality
from indy_client.test.client import TestClient
from indy_client.test.helper import getClientAddedWithRole
from indy_node.test.conftest import nodeThetaAdded
from indy_node.test.helper import TestNode


def test_requests_post_multiple_new_nodes(
        looper,
        tdirWithPoolTxns,
        tdirWithDomainTxnsUpdated,
        nodeSet,
        tconf,
        trustee,
        trusteeWallet,
        allPluginsPath,
        some_transactions_done):
    new_nodes = []
    for node_name in ('Zeta', 'Eta'):
        new_steward, new_steward_wallet, new_node = nodeThetaAdded(looper,
                                                                   nodeSet,
                                                                   tdirWithPoolTxns,
                                                                   tconf,
                                                                   trustee,
                                                                   trusteeWallet,
                                                                   allPluginsPath,
                                                                   TestNode,
                                                                   TestClient,
                                                                   tdirWithPoolTxns,
                                                                   node_name=node_name)
        new_nodes.append((new_steward, new_steward_wallet, new_node))

    for _ in range(5):
        getClientAddedWithRole(nodeSet, tdirWithPoolTxns, looper, trustee,
                               trusteeWallet, randomString(6))

    for (_, _, new_node) in new_nodes:
        waitNodeDataEquality(looper, new_node, *nodeSet[:-2])

    for _ in range(5):
        getClientAddedWithRole(nodeSet, tdirWithPoolTxns, looper, trustee,
                               trusteeWallet, randomString(6))
