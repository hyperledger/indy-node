from indy_node.server.pool_config import PoolConfig

from indy_common.constants import CONFIG_LEDGER_ID
from indy_node.server.upgrader import Upgrader
from plenum.common.txn_util import is_forced
from plenum.server.batch_handlers.batch_request_handler import BatchRequestHandler
from plenum.server.database_manager import DatabaseManager


class ConfigBatchHandler(BatchRequestHandler):
    def __init__(self, database_manager: DatabaseManager,
                 upgrader: Upgrader, pool_config: PoolConfig):
        super().__init__(database_manager, CONFIG_LEDGER_ID)
        self.upgrader = upgrader
        self.pool_config = pool_config

    def commit_batch(self, txn_count, state_root, txn_root, pp_time, prev_result):
        committed_txns = super().commit_batch(txn_count, state_root, txn_root, pp_time, prev_result)
        for txn in committed_txns:
            # Handle POOL_UPGRADE or POOL_CONFIG transaction here
            # only in case it is not forced.
            # If it is forced then it was handled earlier
            # in applyForced method.
            if not is_forced(txn):
                self.upgrader.handleUpgradeTxn(txn)
                self.pool_config.handleConfigTxn(txn)
        return committed_txns
