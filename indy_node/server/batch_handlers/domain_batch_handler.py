from collections import Callable

import base58

from plenum.server.batch_handlers.domain_batch_handler import DomainBatchHandler as PDomainBatchHandler
from plenum.server.database_manager import DatabaseManager


class DomainBatchHandler(PDomainBatchHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager)
        self.post_batch_creation_handlers = []
        self.post_batch_commit_handlers = []
        self.post_batch_rejection_handlers = []

        self._add_default_handlers()

    def commit_batch(self, txn_count, state_root, txn_root, pp_time):
        result = super().commit_batch(txn_count, state_root, txn_root, pp_time)
        self.post_batch_commited(state_root)
        return result

    def post_batch_applied(self, state_root):
        for handler in self.post_batch_creation_handlers:
            handler(state_root)

    def post_batch_rejected(self):
        for handler in self.post_batch_rejection_handlers:
            handler()

    def post_batch_commited(self, state_root):
        for handler in self.post_batch_commit_handlers:
            handler(state_root)

    def _add_default_handlers(self):
        self._add_default_post_batch_creation_handlers()
        self._add_default_post_batch_commit_handlers()
        self._add_default_post_batch_rejection_handlers()

    def _add_default_post_batch_creation_handlers(self):
        self.add_post_batch_creation_handler(self.database_manager.idr_cache.currentBatchCreated)

    def add_post_batch_creation_handler(self, handler: Callable):
        if handler in self.post_batch_creation_handlers:
            raise ValueError('There is already a post batch create handler '
                             'registered {}'.format(handler))
        self.post_batch_creation_handlers.append(handler)

    def _add_default_post_batch_commit_handlers(self):
        self.add_post_batch_commit_handler(self.update_idr_cache)

    def add_post_batch_commit_handler(self, handler: Callable):
        if handler in self.post_batch_commit_handlers:
            raise ValueError('There is already a post batch commit handler '
                             'registered {}'.format(handler))
        self.post_batch_commit_handlers.append(handler)

    def _add_default_post_batch_rejection_handlers(self):
        self.add_post_batch_rejection_handler(self.database_manager.idr_cache.batchRejected)

    def add_post_batch_rejection_handler(self, handler: Callable):
        if handler in self.post_batch_rejection_handlers:
            raise ValueError('There is already a post batch reject handler '
                             'registered {}'.format(handler))
        self.post_batch_rejection_handlers.append(handler)

    def update_idr_cache(self, stateRoot):
        stateRoot = base58.b58decode(stateRoot.encode())
        self.database_manager.idr_cache.onBatchCommitted(stateRoot)
