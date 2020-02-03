from typing import Optional
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SET_RS_CRED_DEF, \
    RS_META, RS_META_VERSION, RS_DATA, RS_META_NAME, DOMAIN_LEDGER_ID, RS_CRED_DEF_FROM, RS_CRED_DEF_MAPPING, \
    RS_CRED_DEF_CONTEXT, SCHEMA, SET_MAPPING, SET_CONTEXT, RS_CRED_DEF_SIGNATURE_TYPE, RS_CRED_DEF

from indy_common.state.state_constants import MARKER_RS_CRED_DEF
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class RsCredDefHandler(WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, SET_RS_CRED_DEF, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        pass

    @staticmethod
    def validate_encoding(encoding):
        pass

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        operation = request.operation
        data = operation[RS_DATA]
        cred_def_txn = data[RS_CRED_DEF]
        mapping_ref = cred_def_txn[RS_CRED_DEF_MAPPING]
        RsCredDefHandler.check_sequence_number(request, mapping_ref, SET_MAPPING)
        context_ref = cred_def_txn[RS_CRED_DEF_CONTEXT]
        RsCredDefHandler.check_sequence_number(request, context_ref, SET_CONTEXT)
        signature_type = cred_def_txn[RS_CRED_DEF_SIGNATURE_TYPE]
        author = request.identifier
        meta = operation[RS_META]
        name = meta[RS_META_NAME]
        version = meta[RS_META_VERSION]
        state_path = RsCredDefHandler.make_state_path(author, name, version, signature_type, mapping_ref, context_ref)
        cred_def, _, _ = self.get_from_state(state_path)
        if cred_def:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=SET_RS_CRED_DEF,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=SET_RS_CRED_DEF,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RsCredDefHandler.prepare_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = RsCredDefHandler.prepare_state(txn)
        self.state.set(path, value_bytes)

    def check_sequence_number(self, request: Request, ref, txn_type):
        try:
            txn = self.ledger.get_by_seq_no_uncommitted(ref)
        except KeyError:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Invalid Sequence number:{}, does not exist.".format(ref))
        if txn['txn']['type'] != txn_type:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Invalid Sequence number:{}, is not a {} reference.".format(ref, txn_type))

    @staticmethod
    def prepare_state(txn, path_only=False):
        payload = txn["txn"]
        operation = payload["data"]
        meta, data = operation[RS_META], operation[RS_DATA]
        cred_def = data[RS_CRED_DEF]
        name, version = meta[RS_META_NAME], meta[RS_META_VERSION]
        did_author = payload["metadata"][RS_CRED_DEF_FROM]
        signature_type = cred_def[RS_CRED_DEF_SIGNATURE_TYPE]
        mapping_ref = cred_def[RS_CRED_DEF_MAPPING]
        context_ref = cred_def[RS_CRED_DEF_MAPPING]
        _id = RsCredDefHandler.make_state_path(did_author,  name, version, signature_type, mapping_ref, context_ref)
        if path_only:
            return _id
        value = {
            RS_META: meta,
            RS_DATA: data
        }
        seq_no = txn["txnMetadata"].get("seqNo", None)
        txn_time = txn["txnMetadata"].get("txnTime", None)
        value_bytes = encode_state_value(value, seq_no, txn_time)
        return _id, value_bytes

    @staticmethod
    def make_state_path(authors_did, name, version, signature_type, mapping_seq_no, context_ref) -> bytes:
        return "{DID}:{MARKER}:{NAME}:{VERSION}:{SIGNATURE_TYPE}:{MAPPING_SEQ_NO}:{CONTEXT_SEQ_NO}" \
            .format(DID=authors_did,
                    MARKER=MARKER_RS_CRED_DEF,
                    NAME=name,
                    VERSION=version,
                    SIGNATURE_TYPE=signature_type,
                    MAPPING_SEQ_NO=mapping_seq_no,
                    CONTEXT_SEQ_NO=context_ref).encode()
