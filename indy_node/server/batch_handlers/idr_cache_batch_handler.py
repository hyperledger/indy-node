import base58

from plenum.server.batch_handlers.batch_request_handler import BatchRequestHandler
from plenum.server.database_manager import DatabaseManager


class IdrCacheBatchHandler(BatchRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, None)

    def commit_batch(self, txn_count, state_root, txn_root, pp_time):
        state_root = base58.b58decode(state_root.encode())
        self.database_manager.idr_cache.update_idr_cache(state_root)

    def post_batch_applied(self, state_root):
        self.database_manager.idr_cache.currentBatchCreated(state_root)

    def post_batch_rejected(self):
        self.database_manager.idr_cache.batchRejected()
