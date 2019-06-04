from copy import deepcopy
from typing import Dict, Callable


from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, VALUE, ISSUANCE_TYPE
from indy_common.state.state_constants import MARKER_REVOC_REG_ENTRY, MARKER_REVOC_REG_ENTRY_ACCUM
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_handler import GetRevocRegHandler
from plenum.common.constants import DOMAIN_LEDGER_ID, TXN_TIME
from plenum.common.request import Request
from plenum.common.txn_util import get_from, get_payload_data, get_req_id, get_request_data, get_txn_time, get_seq_no
from plenum.common.types import f

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class RevocRegEntryHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 get_revoc_reg_entry: GetRevocRegHandler,
                 get_revocation_strategy: Callable):
        super().__init__(database_manager, REVOC_REG_ENTRY, DOMAIN_LEDGER_ID)
        self.get_revoc_reg_entry = get_revoc_reg_entry
        self.get_revocation_strategy = get_revocation_strategy

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        current_entry, revoc_def = self.get_revoc_reg_entry.get_current_revoc_entry_and_revoc_def(
            author_did=identifier,
            revoc_reg_def_id=operation[REVOC_REG_DEF_ID],
            req_id=req_id
        )
        validator_cls = self.get_revocation_strategy(revoc_def[VALUE][ISSUANCE_TYPE])
        validator = validator_cls(self.state)
        validator.validate(current_entry, request)

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RevocRegEntryHandler.prepare_revoc_reg_entry_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, is_committed=False):
        self._validate_txn_type(txn)
        current_entry, revoc_def = self.get_revoc_reg_entry.get_current_revoc_entry_and_revoc_def(
            author_did=get_from(txn),
            revoc_reg_def_id=get_payload_data(txn)[REVOC_REG_DEF_ID],
            req_id=get_req_id(txn)
        )
        writer_cls = self.get_revocation_strategy(
            revoc_def[VALUE][ISSUANCE_TYPE])
        writer = writer_cls(self.state)
        writer.write(current_entry, txn)

    @staticmethod
    def prepare_revoc_reg_entry_for_state(txn, path_only=False):
        author_did = get_from(txn)
        txn_data = get_payload_data(txn)
        revoc_reg_def_id = txn_data.get(REVOC_REG_DEF_ID)
        assert author_did
        assert revoc_reg_def_id
        path = RevocRegEntryHandler.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        if path_only:
            return path

        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        assert seq_no
        assert txn_time
        # TODO: do not duplicate seqNo here
        # doing this now just for backward-compatibility
        txn_data = deepcopy(txn_data)
        txn_data[f.SEQ_NO.nm] = seq_no
        txn_data[TXN_TIME] = txn_time
        value_bytes = encode_state_value(txn_data, seq_no, txn_time)
        return path, value_bytes

    @staticmethod
    def make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id) -> bytes:
        return "{MARKER}:{REVOC_REG_DEF_ID}" \
            .format(MARKER=MARKER_REVOC_REG_ENTRY_ACCUM,
                    REVOC_REG_DEF_ID=revoc_reg_def_id).encode()

    @staticmethod
    def make_state_path_for_revoc_reg_entry(revoc_reg_def_id) -> bytes:
        return "{MARKER}:{REVOC_REG_DEF_ID}" \
            .format(MARKER=MARKER_REVOC_REG_ENTRY,
                    REVOC_REG_DEF_ID=revoc_reg_def_id).encode()


