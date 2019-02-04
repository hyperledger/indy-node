from indy_common.types import Request
from plenum.common.txn_util import append_txn_metadata
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class ConfigWriteRequestHandler(WriteRequestHandler):

    def apply_request(self, request: Request, batch_ts, prev_result):
        self._validate_request_type(request)
        txn = append_txn_metadata(self._req_to_txn(request),
                                  txn_time=batch_ts)
        self.ledger.append_txns_metadata([txn])
        (start, _), _ = self.ledger.appendTxns([txn])
        return start, txn
