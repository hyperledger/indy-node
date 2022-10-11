from typing import Optional

from common.serializers.serialization import config_state_serializer
from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import (
    FLAG,
    CONFIG_LEDGER_ID,
    FLAG_NAME,
    FLAG_VALUE,
)
from indy_common.state.state_constants import LAST_SEQ_NO, LAST_UPDATE_TIME, MARKER_FLAG
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import (
    get_payload_data,
    get_seq_no,
    get_txn_time,
)
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import (
    WriteRequestHandler,
)


class FlagRequestHandler(WriteRequestHandler):
    def __init__(
        self,
        database_manager: DatabaseManager,
        write_req_validator: WriteRequestValidator,
    ):
        super().__init__(database_manager, FLAG, CONFIG_LEDGER_ID)
        self.write_req_validator = write_req_validator
        self.state_serializer = config_state_serializer

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        name = request.operation.get(FLAG_NAME)
        value = request.operation.get(FLAG_VALUE)
        if not name:
            raise InvalidClientRequest(
                request.identifier, request.reqId, "Flag name is required"
            )
        if not isinstance(name, str):
            raise InvalidClientRequest(
                request.identifier, request.reqId, "Flag name must be of type string"
            )
        if not (isinstance(value, str) or (value is None)):
            raise InvalidClientRequest(
                request.identifier, request.reqId, "Flag value must be of type string or None"
            )

    def additional_dynamic_validation(
        self, request: Request, req_pp_time: Optional[int]
    ):
        self._validate_request_type(request)
        self.write_req_validator.validate(request, [AuthActionEdit(txn_type=FLAG)])

    def update_state(self, txn, prev_result, request, is_committed=False):
        self._validate_txn_type(txn)
        key = get_payload_data(txn).get(FLAG_NAME)
        value = get_payload_data(txn).get(FLAG_VALUE)
        state = {}
        state[FLAG_VALUE] = value
        state[LAST_SEQ_NO] = get_seq_no(txn)
        state[LAST_UPDATE_TIME] = get_txn_time(txn)
        val = self.state_serializer.serialize(state)
        path = self.make_state_path_for_flag(key)
        self.state.set(path, val)
        return state

    @staticmethod
    def make_state_path_for_flag(key) -> bytes:
        return "{MARKER}:{FLAG}".format(MARKER=MARKER_FLAG, FLAG=key).encode()

    @staticmethod
    def get_state_value(state_raw):
        if state_raw is None:
            return state_raw
        return state_raw.get(FLAG_VALUE)
