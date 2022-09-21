from typing import Optional

from common.serializers.serialization import config_state_serializer
from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import (
    FLAG,
    CONFIG_LEDGER_ID,
    DOMAIN_LEDGER_ID,
    FLAG_NAME,
    FLAG_VALUE,
    FLAG_TIME,
)
from indy_common.state.state_constants import MARKER_FLAG
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_txn_time, get_seq_no
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import (
    WriteRequestHandler,
)
from plenum.server.request_handlers.utils import encode_state_value, is_trustee


class FlagHandler(WriteRequestHandler):
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
        if not name or name == "":
            raise InvalidClientRequest(
                request.identifier, request.reqId, "Flag name is required"
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
        time = get_txn_time(txn)
        val = {FLAG_TIME: time, FLAG_VALUE: value}
        val = self.state_serializer.serialize(val)
        self.state.set(self.make_state_path_for_flag(key), val)

    def _decode_state_value(self, encoded):
        if encoded:
            return self.state_serializer.deserialize(encoded)
        return None

    def authorize(self, request):
        domain_state = self.database_manager.get_database(DOMAIN_LEDGER_ID).state
        if not is_trustee(domain_state, request.identifier, is_committed=False):
            raise UnauthorizedClientRequest(
                request.identifier, request.reqId, "Only trustee can set config flags"
            )

    def get_state(self, key):
        if key is None or key == "":
            return None, None
        path = FlagHandler.make_state_path_for_flag(key)
        state = self.get_from_state(path)
        value = FlagHandler.get_state_value(state)
        timestamp = FlagHandler.get_state_timestamp(state)
        return (value, timestamp)

    @staticmethod
    def make_state_path_for_flag(key) -> bytes:
        return "{MARKER}:{FLAG}".format(MARKER=MARKER_FLAG, FLAG=key).encode()

    @staticmethod
    def get_state_timestamp(state_raw):
        return state_raw.get(FLAG_TIME)

    @staticmethod
    def get_state_value(state_raw):
        return state_raw.get(FLAG_VALUE)
