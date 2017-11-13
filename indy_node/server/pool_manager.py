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

from plenum.common.constants import POOL_LEDGER_ID, DOMAIN_LEDGER_ID
from plenum.server.pool_manager import HasPoolManager as PHasPoolManager, \
    TxnPoolManager as PTxnPoolManager
from indy_node.server.pool_req_handler import PoolRequestHandler


class HasPoolManager(PHasPoolManager):
    # noinspection PyUnresolvedReferences, PyTypeChecker
    def __init__(self, nodeRegistry=None, ha=None, cliname=None, cliha=None):
        if not nodeRegistry:
            self.poolManager = TxnPoolManager(self, ha=ha, cliname=cliname,
                                              cliha=cliha)
            self.requestExecuter[POOL_LEDGER_ID] = \
                self.poolManager.executePoolTxnBatch
        else:
            super().__init__(nodeRegistry=nodeRegistry, ha=ha, cliname=cliname,
                             cliha=cliha)


class TxnPoolManager(PTxnPoolManager):
    def __init__(self, node, ha=None, cliname=None, cliha=None):
        super().__init__(node=node, ha=ha, cliname=cliname, cliha=cliha)

    def getPoolReqHandler(self):
        return PoolRequestHandler(self.ledger, self.state,
                                  self.node.states[DOMAIN_LEDGER_ID],
                                  self.node.getIdrCache())
