from copy import deepcopy
from typing import Callable, Optional

from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from indy_common.constants import FLAG_NAME_COMPAT_ORDERING, REVOC_REG_ENTRY, REVOC_REG_DEF_ID, VALUE, ISSUANCE_TYPE
from indy_common.state.state_constants import MARKER_REVOC_REG_ENTRY, MARKER_REVOC_REG_ENTRY_ACCUM
from indy_node.server.request_handlers.read_req_handlers.get_flag_handler import GetFlagRequestHandler
from plenum.common.constants import DOMAIN_LEDGER_ID, TXN_TIME
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_from, get_payload_data, get_req_id, get_request_data, get_txn_time, get_seq_no
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value
from plenum.server.node import Node

from indy_node.server.request_handlers.config_req_handlers.flag_handler import FlagRequestHandler


class RevocRegEntryHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator,
                 get_revocation_strategy: Callable,
                 node: Node):
        super().__init__(database_manager, REVOC_REG_ENTRY, DOMAIN_LEDGER_ID)
        self.get_revocation_strategy = get_revocation_strategy
        self.write_req_validator = write_req_validator
        # Default sorting behavior
        self.legacy_sort_config = getConfig().REV_STRATEGY_USE_COMPAT_ORDERING or False
        # Create a local GetFlagRequestHandler to allow lookups for the config flag
        get_flag_handler = GetFlagRequestHandler(node=node,
                                                 database_manager=database_manager)
        self.get_flag_handler = get_flag_handler

    def use_legacy_sort(self, txn) -> bool:
        txn_time = get_txn_time(txn)
        state_raw = self.get_flag_handler.lookup_key(FLAG_NAME_COMPAT_ORDERING, timestamp=txn_time)
        sort_state = FlagRequestHandler.get_state_value(state_raw)
        if sort_state and isinstance(sort_state, str):
            # only allow False as value, ignore otherwise
            if sort_state.lower() == 'false':
                return False
        # default to default behavior
        return self.legacy_sort_config

    def static_validation(self, request: Request):
        pass

    def additional_dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)
        rev_reg_tags = request.operation[REVOC_REG_DEF_ID]
        author_did, req_id, operation = get_request_data(request)
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=author_did,
            revoc_reg_def_id=operation[REVOC_REG_DEF_ID],
            req_id=req_id
        )
        rev_ref_def_author_did = rev_reg_tags.split(":", 1)[0]
        is_owner = rev_ref_def_author_did == author_did

        if current_entry:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=REVOC_REG_ENTRY,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*',
                                                              is_owner=is_owner)])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=REVOC_REG_ENTRY,
                                                             field='*',
                                                             value='*',
                                                             is_owner=is_owner)])
        validator_cls = self.get_revocation_strategy(revoc_def[VALUE][ISSUANCE_TYPE])
        validator = validator_cls(self.state)
        validator.validate(current_entry, request)

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RevocRegEntryHandler.prepare_revoc_reg_entry_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False):
        self._validate_txn_type(txn)
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=get_from(txn),
            revoc_reg_def_id=get_payload_data(txn)[REVOC_REG_DEF_ID],
            req_id=get_req_id(txn)
        )
        writer_cls = self.get_revocation_strategy(
            revoc_def[VALUE][ISSUANCE_TYPE])

        sort_legacy = self.use_legacy_sort(txn)
        writer = writer_cls(self.state, sort_legacy)
        writer.write(current_entry, txn)
        return txn

    def _get_current_revoc_entry_and_revoc_def(self, author_did, revoc_reg_def_id, req_id):
        assert revoc_reg_def_id
        current_entry, _, _ = self._get_revoc_def_entry(revoc_reg_def_id=revoc_reg_def_id)
        revoc_def, _, _ = self.get_from_state(revoc_reg_def_id)
        if revoc_def is None:
            raise InvalidClientRequest(author_did,
                                       req_id,
                                       "There is no any REVOC_REG_DEF by path: {}".format(revoc_reg_def_id))
        return current_entry, revoc_def

    def _get_revoc_def_entry(self,
                             revoc_reg_def_id) -> (str, int, int):
        assert revoc_reg_def_id
        path = RevocRegEntryHandler.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        try:
            keys, seq_no, last_update_time = self.get_from_state(path)
            return keys, seq_no, last_update_time
        except KeyError:
            return None, None, None, None

    @staticmethod
    def prepare_revoc_reg_entry_accum_for_state(txn):
        author_did = get_from(txn)
        txn_data = get_payload_data(txn)
        revoc_reg_def_id = txn_data.get(REVOC_REG_DEF_ID)
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        assert author_did
        assert revoc_reg_def_id
        assert seq_no
        assert txn_time
        path = RevocRegEntryHandler.make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id)

        # TODO: do not duplicate seqNo here
        # doing this now just for backward-compatibility
        txn_data = deepcopy(txn_data)
        txn_data[f.SEQ_NO.nm] = seq_no
        txn_data[TXN_TIME] = txn_time
        value_bytes = encode_state_value(txn_data, seq_no, txn_time)
        return path, value_bytes

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
