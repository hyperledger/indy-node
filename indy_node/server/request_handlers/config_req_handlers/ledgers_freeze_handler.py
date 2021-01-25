from typing import Optional

from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import CONFIG_LEDGER_ID, LEDGERS_FREEZE, LEDGERS_IDS

from common.serializers.serialization import config_state_serializer
from indy_common.state.config import MARKER_FROZEN_LEDGERS
from plenum.common.constants import CONFIG_LEDGER_ID, AUDIT_LEDGER_ID, AUDIT_TXN_NODE_REG, AUDIT_TXN_LEDGER_ROOT, \
    AUDIT_TXN_STATE_ROOT, AUDIT_TXN_LEDGERS_SIZE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class LedgersFreezeHandler(WriteRequestHandler):
    state_serializer = config_state_serializer

    LEDGER = "ledger"
    STATE = "state"
    SEQ_NO = "seq_no"

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, LEDGERS_FREEZE, CONFIG_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        # TODO: add a check that ledgers_ids doesn't contains base ledgers

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)
        self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=LEDGERS_FREEZE,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        # TODO: add a check for existing ledgers_ids in audit

    def update_state(self, txn, prev_result, request, is_committed=False):
        self._validate_txn_type(txn)
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        ledgers_ids = get_payload_data(txn)[LEDGERS_IDS]
        frozen_ledgers = self.make_frozen_ledgers_list(ledgers_ids)
        self.state.set(self.make_state_path_for_frozen_ledgers(), encode_state_value(frozen_ledgers, seq_no, txn_time))
        return txn

    @staticmethod
    def make_state_path_for_frozen_ledgers() -> bytes:
        return "{MARKER}:FROZEN_LEDGERS" \
            .format(MARKER=MARKER_FROZEN_LEDGERS).encode()

# TODO: add getting root hashes from audit
    def make_frozen_ledgers_list(self, ledgers_ids):
        ledger_root, state_root, seq_no = self.__load_hash_roots_from_audit_ledger()
        return {ledger_id: {LedgersFreezeHandler.LEDGER: ledger_root,
                            LedgersFreezeHandler.STATE: state_root,
                            LedgersFreezeHandler.SEQ_NO: seq_no} for ledger_id in ledgers_ids}

    def __load_hash_roots_from_audit_ledger(self):
        audit_ledger = self.database_manager.get_ledger(AUDIT_LEDGER_ID)
        if not audit_ledger:
            return None, None, None

        last_txn = audit_ledger.get_last_committed_txn()
        last_txn_ledger_root = get_payload_data(last_txn).get(AUDIT_TXN_LEDGER_ROOT, None)
        last_txn_state_root = get_payload_data(last_txn).get(AUDIT_TXN_STATE_ROOT, None)
        last_txn_seq_no = get_payload_data(last_txn).get(AUDIT_TXN_LEDGERS_SIZE, None)

        if isinstance(last_txn_ledger_root, int):
            seq_no = get_seq_no(last_txn) - last_txn_ledger_root
            audit_txn_for_seq_no = audit_ledger.getBySeqNo(seq_no)
            last_txn_ledger_root = get_payload_data(audit_txn_for_seq_no).get(AUDIT_TXN_LEDGER_ROOT)

        if isinstance(last_txn_state_root, int):
            seq_no = get_seq_no(last_txn) - last_txn_ledger_root
            audit_txn_for_seq_no = audit_ledger.getBySeqNo(seq_no)
            last_txn_state_root = get_payload_data(audit_txn_for_seq_no).get(AUDIT_TXN_STATE_ROOT)

        return last_txn_ledger_root, last_txn_state_root, last_txn_seq_no
