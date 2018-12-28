from indy_common.constants import TIMESTAMP, REVOC_REG_DEF_ID, GET_REVOC_REG

from indy_common.state import domain

from indy_node.server.request_handlers.utils import StateValue
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetRevocRegHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_REVOC_REG, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        req_ts = request.operation.get(TIMESTAMP)
        revoc_reg_def_id = request.operation.get(REVOC_REG_DEF_ID)
        # Get root hash corresponding with given timestamp
        past_root = self.database_manager.ts_store.get_equal_or_prev(req_ts)
        # Path to corresponding ACCUM record in state
        path = domain.make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)
        entry_state = StateValue()
        if past_root is not None:
            encoded_entry, proof = self._get_value_from_state(path,
                                                              head_hash=past_root,
                                                              with_proof=True)
            entry_state.proof = proof
            if encoded_entry:
                revoc_reg_entry_accum, seq_no, last_update_time = domain.decode_state_value(encoded_entry)
                entry_state = StateValue(root_hash=past_root,
                                         value=revoc_reg_entry_accum,
                                         seq_no=seq_no,
                                         update_time=last_update_time,
                                         proof=proof)

        return self.make_result(request=request,
                                data=entry_state.value,
                                last_seq_no=entry_state.seq_no,
                                update_time=entry_state.update_time,
                                proof=entry_state.proof)

    def get_current_revoc_entry_and_revoc_def(self, author_did, revoc_reg_def_id, req_id):
        assert revoc_reg_def_id
        current_entry, _, _, _ = self._get_revoc_def_entry(revoc_reg_def_id=revoc_reg_def_id,
                                                           is_committed=False)
        revoc_def, _, _, _ = self.lookup(revoc_reg_def_id, is_committed=False, with_proof=False)
        if revoc_def is None:
            raise InvalidClientRequest(author_did,
                                       req_id,
                                       "There is no any REVOC_REG_DEF by path: {}".format(revoc_reg_def_id))
        return current_entry, revoc_def

    def _get_revoc_def_entry(self,
                             revoc_reg_def_id,
                             is_committed=True) -> (str, int, int, list):
        assert revoc_reg_def_id
        path = domain.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        try:
            keys, seq_no, last_update_time, proof = self.lookup(path, is_committed, with_proof=True)
            return keys, seq_no, last_update_time, proof
        except KeyError:
            return None, None, None, None
