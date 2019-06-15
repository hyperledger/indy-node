from indy_common.constants import NYM, ROLE
from indy_common.types import Request
from plenum.common.constants import TARGET_NYM, VERKEY
from plenum.common.txn_util import get_txn_time, get_payload_data, get_seq_no
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class IdrCacheNymHandler(WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, NYM, None)

    def apply_request(self, request: Request, batch_ts, prev_result):
        txn = self._req_to_txn(request)
        self.update_state(txn, prev_result, request)

    def update_state(self, txn, prev_result, request, is_committed=False):
        txn_time = get_txn_time(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        self.database_manager.idr_cache.set(nym,
                                            seqNo=get_seq_no(txn),
                                            txnTime=txn_time,
                                            ta=prev_result.get(f.IDENTIFIER.nm),
                                            role=prev_result.get(ROLE),
                                            verkey=prev_result.get(VERKEY),
                                            isCommitted=is_committed)

    def static_validation(self, request):
        pass

    def dynamic_validation(self, request):
        pass

    def gen_state_key(self, txn):
        pass
