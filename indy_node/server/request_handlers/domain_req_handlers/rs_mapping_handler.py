from typing import Optional
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SET_RS_MAPPING, \
    RS_META, RS_META_VERSION, RS_DATA, RS_META_NAME, DOMAIN_LEDGER_ID, RS_MAPPING_FROM, RS_MAPPING, \
    RS_MAPPING_SCHEMA_REF

from indy_common.state.state_constants import MARKER_RS_SCHEMA
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class RsMappingHandler(WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, SET_RS_MAPPING, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        pass

    @staticmethod
    def validate_schema(schema):
        pass

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        operation = request.operation
        data = operation[RS_DATA]
        mapping_txn = data[RS_MAPPING]
        schema_refs = mapping_txn[RS_MAPPING_SCHEMA_REF]
        for ref in schema_refs:
            RsMappingHandler.check_sequence_number(request, ref, SET_RS_MAPPING)
        author = request.identifier
        name = request.operation[RS_META][RS_META_NAME]
        version = request.operation[RS_META][RS_META_VERSION]
        state_path = RsMappingHandler.make_state_path(author, name, version, schema_refs)
        mapping, _, _ = self.get_from_state(state_path)
        if mapping:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=SET_RS_MAPPING,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=SET_RS_MAPPING,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RsMappingHandler.prepare_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = RsMappingHandler.prepare_state(txn)
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
        meta, data = payload["data"][RS_META], payload["data"][RS_DATA]
        name, version = meta[RS_META_NAME], meta[RS_META_VERSION]
        did_author = payload["metadata"][RS_MAPPING_FROM]
        schemas = data[RS_MAPPING_SCHEMA_REF]
        _id = RsMappingHandler.make_state_path(did_author, name, version, schemas)
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
    def make_state_path(authors_did, name, version, schema_refs) -> bytes:
        return "{DID}:{MARKER}:{NAME}:{VERSION}:{RS_SCHEMA_SEQ_NO}" \
            .format(DID=authors_did,
                    MARKER=MARKER_RS_SCHEMA,
                    NAME=name,
                    VERSION=version,
                    RS_SCHEMA_SEQ_NO="-".join(schema_refs.sort).encode())
