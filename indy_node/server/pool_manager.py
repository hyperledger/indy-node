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
