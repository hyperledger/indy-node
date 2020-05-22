from typing import Optional

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SCHEMA, SCHEMA_ATTR_NAMES

from indy_common.req_utils import get_write_schema_name, get_write_schema_version, get_txn_schema_name, \
    get_txn_schema_version, get_txn_schema_attr_names
from indy_common.state.state_constants import MARKER_SCHEMA
from plenum.common.constants import DOMAIN_LEDGER_ID

from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_from, get_seq_no, get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class SchemaHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, SCHEMA, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        # we can not add a Schema with already existent NAME and VERSION
        # sine a Schema needs to be identified by seqNo
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        schema_name = get_write_schema_name(request)
        schema_version = get_write_schema_version(request)
        path = SchemaHandler.make_state_path_for_schema(identifier, schema_name, schema_version)
        schema, _, _ = self.get_from_state(path)
        if schema:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=SCHEMA,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=SCHEMA,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = SchemaHandler.prepare_schema_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = SchemaHandler.prepare_schema_for_state(txn)
        self.state.set(path, value_bytes)
        return txn

    @staticmethod
    def prepare_schema_for_state(txn, path_only=False):
        origin = get_from(txn)
        schema_name = get_txn_schema_name(txn)
        schema_version = get_txn_schema_version(txn)
        value = {
            SCHEMA_ATTR_NAMES: get_txn_schema_attr_names(txn)
        }
        path = SchemaHandler.make_state_path_for_schema(origin, schema_name, schema_version)
        if path_only:
            return path
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        value_bytes = encode_state_value(value, seq_no, txn_time)
        return path, value_bytes

    @staticmethod
    def make_state_path_for_schema(authors_did, schema_name, schema_version) -> bytes:
        return "{DID}:{MARKER}:{SCHEMA_NAME}:{SCHEMA_VERSION}" \
            .format(DID=authors_did,
                    MARKER=MARKER_SCHEMA,
                    SCHEMA_NAME=schema_name,
                    SCHEMA_VERSION=schema_version).encode()
