import base58
from indy_common.constants import ROLE
from plenum.common.constants import VERKEY, TARGET_NYM

from plenum.common.request import Request
from plenum.common.txn_util import get_txn_time, get_seq_no, get_payload_data
from plenum.common.types import f
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler

from plenum.server.batch_handlers.batch_request_handler import BatchRequestHandler
from plenum.server.database_manager import DatabaseManager


class IdrCacheHandler(BatchRequestHandler, WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, None)

    def commit_batch(self, ledger_id, txn_count, state_root, txn_root, pp_time, prev_handler_result=None):
        state_root = base58.b58decode(state_root.encode())
        self.database_manager.idr_cache.update_idr_cache(state_root)

    def post_batch_applied(self, three_pc_batch, prev_handler_result=None):
        self.database_manager.idr_cache.currentBatchCreated(three_pc_batch.state_root)

    def post_batch_rejected(self, ledger_id, prev_handler_result=None):
        self.database_manager.idr_cache.batchRejected()

    def apply_request(self, request: Request, batch_ts, prev_result):
        txn = self._req_to_txn(request)
        self.update_state(txn, prev_result)

    def update_state(self, txn, prev_result, is_committed=False):
        txn_time = get_txn_time(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        self.database_manager.idr_cache.set(nym,
                                            seqNo=get_seq_no(txn),
                                            txnTime=txn_time,
                                            ta=prev_result.get(f.IDENTIFIER.nm),
                                            role=prev_result.get(ROLE),
                                            verkey=prev_result.get(VERKEY),
                                            isCommitted=is_committed)
