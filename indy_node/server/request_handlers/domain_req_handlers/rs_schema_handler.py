from typing import Optional
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SET_RS_SCHEMA, \
    RS_META, RS_META_VERSION, RS_DATA, RS_META_NAME, DOMAIN_LEDGER_ID, RS_SCHEMA_FROM

from indy_common.state.state_constants import MARKER_RS_SCHEMA

from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value
from stp_core.common.log import getlogger

logger = getlogger()


class RsSchemaHandler(WriteRequestHandler):
    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, SET_RS_SCHEMA, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        pass

    @staticmethod
    def validate_schema(schema):
        pass

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        logger.trace(
            "{} entering rs schema dynamic_validation with {}"
            "".format(self, request)
        )
        self._validate_request_type(request)
        author = request.identifier
        name = request.operation[RS_META][RS_META_NAME]
        version = request.operation[RS_META][RS_META_VERSION]
        state_path = RsSchemaHandler.make_state_path(author, name, version)
        schema, _, _ = self.get_from_state(state_path)
        if schema:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=SET_RS_SCHEMA,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=SET_RS_SCHEMA,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RsSchemaHandler.prepare_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = RsSchemaHandler.prepare_state(txn)
        self.state.set(path, value_bytes)

    @staticmethod
    def prepare_state(txn, path_only=False):
        payload = txn["txn"]
        meta, data = payload["data"][RS_META], payload["data"][RS_DATA]
        name, version = meta[RS_META_NAME], meta[RS_META_VERSION]
        did_author = payload["metadata"][RS_SCHEMA_FROM]
        _id = RsSchemaHandler.make_state_path(did_author, name, version)
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
    def make_state_path(authors_did, name, version) -> bytes:
        return "{DID}:{MARKER}:{NAME}:{VERSION}" \
            .format(DID=authors_did,
                    MARKER=MARKER_RS_SCHEMA,
                    NAME=name,
                    VERSION=version).encode()
