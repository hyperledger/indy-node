from indy_common.state import domain

from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF, REVOC_REG_DEF_ID, VALUE, ISSUANCE_TYPE
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_handler import GetRevocRegHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.txn_util import get_type, get_from, get_payload_data, get_req_id

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class RevocRegEntryHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 get_revoc_reg_entry: GetRevocRegHandler,
                 revocation_strategy_map: dict):
        super().__init__(database_manager, REVOC_REG_ENTRY, DOMAIN_LEDGER_ID)
        self.get_revoc_reg_entry = get_revoc_reg_entry
        self.revocation_strategy_map = revocation_strategy_map

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        current_entry, revoc_def = self.get_revoc_reg_entry.get_current_revoc_entry_and_revoc_def(
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
        current_entry, revoc_def = self.get_revoc_reg_entry._get_current_revoc_entry_and_revoc_def(
            author_did=get_from(txn),
            revoc_reg_def_id=get_payload_data(txn)[REVOC_REG_DEF_ID],
            req_id=get_req_id(txn)
        )
        writer_cls = self.get_revocation_strategy(
            revoc_def[VALUE][ISSUANCE_TYPE])
        writer = writer_cls(self.state)
        writer.write(current_entry, txn)

    def get_revocation_strategy(self, type):
        return self.revocation_strategy_map.get(type, None)
