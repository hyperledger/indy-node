from collections import Callable

from indy_common.constants import FROM, TO, REVOC_REG_DEF_ID, ISSUANCE_TYPE, REVOKED, ISSUED, VALUE, REVOC_TYPE, \
    ACCUM_TO, STATE_PROOF_FROM, ACCUM_FROM, GET_REVOC_REG_DELTA
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import RevocRegEntryHandler

from indy_node.server.request_handlers.utils import StateValue
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from plenum.server.request_handlers.utils import decode_state_value


class GetRevocRegDeltaHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 get_revocation_strategy: Callable):
        super().__init__(database_manager, GET_REVOC_REG_DELTA, DOMAIN_LEDGER_ID)
        self.get_revocation_strategy = get_revocation_strategy

    def static_validation(self, request: Request):
        operation = request.operation
        req_ts_to = operation.get(TO, None)
        assert req_ts_to
        req_ts_from = operation.get(FROM, None)

        if req_ts_from and req_ts_from > req_ts_to:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Timestamp FROM more then TO: {} > {}".format(req_ts_from, req_ts_to))

    def get_result(self, request: Request):
        """
        For getting reply we need:
        1. Get REVOC_REG_ENTRY by "TO" timestamp from state
        2. If FROM is given in request, then Get REVOC_REG_ENTRY by "FROM" timestamp from state
        3. Get ISSUANCE_TYPE for REVOC_REG_DEF (revoked/issued strategy)
        4. Compute issued and revoked indices by corresponding strategy
        5. Make result
           5.1 Now, if "FROM" is presented in request, then STATE_PROOF_FROM and ACCUM (revocation entry for "FROM" timestamp)
               will added into data section
           5.2 If not, then only STATE_PROOF for "TO" revocation entry will added
        :param request:
        :return: Reply
        """
        self._validate_request_type(request)
        req_ts_from = request.operation.get(FROM, None)
        req_ts_to = request.operation.get(TO)
        revoc_reg_def_id = request.operation.get(REVOC_REG_DEF_ID)
        reply = None
        """
        Get root hash for "to" timestamp
        Get REVOC_REG_ENTRY and ACCUM record for timestamp "to"
        """
        path_to_reg_entry = RevocRegEntryHandler.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        path_to_reg_entry_accum = RevocRegEntryHandler.make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)

        entry_to = self._get_reg_entry_by_timestamp(req_ts_to, path_to_reg_entry)
        accum_to = self._get_reg_entry_accum_by_timestamp(req_ts_to, path_to_reg_entry_accum)
        entry_from = StateValue()
        accum_from = StateValue()

        if accum_to.value and entry_to.value:
            """Get issuance type from REVOC_REG_DEF"""
            encoded_revoc_reg_def = self.state.get_for_root_hash(entry_to.root_hash,
                                                                 revoc_reg_def_id)
            if encoded_revoc_reg_def:
                revoc_reg_def, _, _ = decode_state_value(encoded_revoc_reg_def)
                strategy_cls = self.get_revocation_strategy(revoc_reg_def[VALUE][ISSUANCE_TYPE])
                issued_to = entry_to.value[VALUE].get(ISSUED, [])
                revoked_to = entry_to.value[VALUE].get(REVOKED, [])
                if req_ts_from:
                    """Get REVOC_REG_ENTRY and ACCUM records for timestamp from if exist"""
                    entry_from = self._get_reg_entry_by_timestamp(req_ts_from, path_to_reg_entry)
                    accum_from = self._get_reg_entry_accum_by_timestamp(req_ts_from, path_to_reg_entry_accum)
                if req_ts_from and entry_from.value and accum_from.value:
                    """Compute issued/revoked lists corresponding with ISSUANCE_TYPE strategy"""
                    issued_from = entry_from.value[VALUE].get(ISSUED, [])
                    revoked_from = entry_from.value[VALUE].get(REVOKED, [])
                    result_issued, result_revoked = strategy_cls.get_delta({ISSUED: issued_to,
                                                                            REVOKED: revoked_to},
                                                                           {ISSUED: issued_from,
                                                                            REVOKED: revoked_from})
                else:
                    result_issued, result_revoked = strategy_cls.get_delta({ISSUED: issued_to,
                                                                            REVOKED: revoked_to},
                                                                           None)
                reply = {
                    REVOC_REG_DEF_ID: revoc_reg_def_id,
                    REVOC_TYPE: revoc_reg_def.get(REVOC_TYPE),
                    VALUE: {
                        ACCUM_TO: accum_to.value if entry_from.value else entry_to.value,
                        ISSUED: result_issued,
                        REVOKED: result_revoked
                    }

                }
                """If we got "from" timestamp, then add state proof into "data" section of reply"""
                if req_ts_from:
                    reply[STATE_PROOF_FROM] = accum_from.proof
                    reply[VALUE][ACCUM_FROM] = accum_from.value

        if accum_to and entry_to:
            seq_no = accum_to.seq_no if entry_from.value else entry_to.seq_no
            update_time = accum_to.update_time if entry_from.value else entry_to.update_time
            proof = accum_to.proof if entry_from.value else entry_to.proof
            if reply is None and req_ts_from is not None:
                # TODO: change this according to INDY-2115
                reply = {}
                accum_from = self._get_reg_entry_accum_by_timestamp(req_ts_from, path_to_reg_entry_accum)
                reply[STATE_PROOF_FROM] = accum_from.proof
                reply[VALUE] = {}
                reply[VALUE][ACCUM_TO] = None
                reply[VALUE][ACCUM_FROM] = accum_from.value
        else:
            seq_no = None
            update_time = None
            proof = None

        return self.make_result(request=request,
                                data=reply,
                                last_seq_no=seq_no,
                                update_time=update_time,
                                proof=proof)

    def _get_reg_entry_by_timestamp(self, timestamp, path_to_reg_entry):
        reg_entry = None
        seq_no = None
        last_update_time = None
        reg_entry_proof = None
        past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            encoded_entry, reg_entry_proof = self._get_value_from_state(path_to_reg_entry,
                                                                        head_hash=past_root,
                                                                        with_proof=True)
            if encoded_entry:
                reg_entry, seq_no, last_update_time = decode_state_value(encoded_entry)
        return StateValue(root_hash=past_root,
                          value=reg_entry,
                          seq_no=seq_no,
                          update_time=last_update_time,
                          proof=reg_entry_proof)

    def _get_reg_entry_accum_by_timestamp(self, timestamp, path_to_reg_entry_accum):
        reg_entry_accum = None
        seq_no = None
        last_update_time = None
        reg_entry_accum_proof = None
        past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            encoded_entry, reg_entry_accum_proof = self._get_value_from_state(
                path_to_reg_entry_accum, head_hash=past_root, with_proof=True)
            if encoded_entry:
                reg_entry_accum, seq_no, last_update_time = decode_state_value(encoded_entry)
        return StateValue(root_hash=past_root,
                          value=reg_entry_accum,
                          seq_no=seq_no,
                          update_time=last_update_time,
                          proof=reg_entry_accum_proof)
