import base58
from plenum.common.constants import DOMAIN_LEDGER_ID

from plenum.server.batch_handlers.batch_request_handler import BatchRequestHandler
from plenum.server.batch_handlers.three_pc_batch import ThreePcBatch
from plenum.server.database_manager import DatabaseManager


class IdrCacheBatchHandler(BatchRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, DOMAIN_LEDGER_ID)

    def commit_batch(self, three_pc_batch: ThreePcBatch, prev_handler_result=None):
        state_root = base58.b58decode(three_pc_batch.state_root.encode())
        self.database_manager.idr_cache.onBatchCommitted(state_root)

    def post_batch_applied(self, three_pc_batch: ThreePcBatch, prev_handler_result=None):
        self.database_manager.idr_cache.currentBatchCreated(three_pc_batch.state_root,
                                                            three_pc_batch.pp_time)

    def post_batch_rejected(self, ledger_id, prev_handler_result=None):
        self.database_manager.idr_cache.batchRejected()
