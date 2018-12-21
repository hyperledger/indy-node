from indy_common.constants import REVOC_REG_DEF
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class RevocationRegDefHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, REVOC_REG_DEF, DOMAIN_LEDGER_ID)

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        pass

    def gen_txn_path(self, txn):
        path = domain.prepare_revoc_reg_entry_for_state(txn, path_only=True)
        return path.decode()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False):
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=get_from(txn),
            revoc_reg_def_id=get_payload_data(txn)[REVOC_REG_DEF_ID],
            req_id=get_req_id(txn)
        )
        writer_cls = self.get_revocation_strategy(
            revoc_def[VALUE][ISSUANCE_TYPE])
        writer = writer_cls(self.state)
        writer.write(current_entry, txn)
