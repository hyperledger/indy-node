from indy_common.state import domain

from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF, REVOC_REG_DEF_ID, VALUE, ISSUANCE_TYPE
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.txn_util import get_type

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class RevocRegEntryHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, REVOC_REG_ENTRY, DOMAIN_LEDGER_ID)

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=identifier,
            revoc_reg_def_id=operation[REVOC_REG_DEF_ID],
            req_id=req_id
        )
        validator_cls = self.get_revocation_strategy(revoc_def[VALUE][ISSUANCE_TYPE])
        validator = validator_cls(self.state)
        validator.validate(current_entry, request)

    def gen_txn_path(self, txn):
        path = domain.prepare_revoc_reg_entry_for_state(txn, path_only=True)
        return path.decode()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False):
        assert get_type(txn) == REVOC_REG_DEF
        path, value_bytes = domain.prepare_revoc_def_for_state(txn)
        self.state.set(path, value_bytes)
