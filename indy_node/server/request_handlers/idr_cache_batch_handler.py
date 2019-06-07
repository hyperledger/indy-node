import base58
from plenum.common.constants import DOMAIN_LEDGER_ID

from plenum.server.batch_handlers.batch_request_handler import BatchRequestHandler
from plenum.server.database_manager import DatabaseManager


class IdrCacheBatchHandler(BatchRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, DOMAIN_LEDGER_ID)

    def commit_batch(self, ledger_id, txn_count, state_root, txn_root, pp_time, prev_handler_result=None):
        state_root = base58.b58decode(state_root.encode())
        self.database_manager.idr_cache.update_idr_cache(state_root)

    def post_batch_applied(self, three_pc_batch, prev_handler_result=None):
        self.database_manager.idr_cache.currentBatchCreated(three_pc_batch.state_root)

    def post_batch_rejected(self, ledger_id, prev_handler_result=None):
        self.database_manager.idr_cache.batchRejected()
