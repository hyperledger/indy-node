from typing import Optional

from common.serializers.serialization import config_state_serializer
from indy_common.constants import SET_FEES, FEES
from indy_node.server.request_handlers.config_req_handlers.fees.fees_static_helper import FeesStaticHelper
from plenum.common.constants import CONFIG_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class SetFeesHandler(WriteRequestHandler):

    def __init__(self, db_manager: DatabaseManager, write_req_validator):
        super().__init__(db_manager, SET_FEES, CONFIG_LEDGER_ID)
        self._write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        raise InvalidClientRequest(request.identifier,
                                   request.reqId,
                                   "SET_FEES transactions are forbidden now.")

    def additional_dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        raise InvalidClientRequest(request.identifier,
                                   request.reqId,
                                   "SET_FEES transactions are forbidden now.")

    def update_state(self, txn, prev_result, request, is_committed=False):
        payload = get_payload_data(txn)
        fees_from_req = payload.get(FEES)
        current_fees = FeesStaticHelper.get_fee_from_state(self.state)
        current_fees = current_fees if current_fees else {}
        current_fees.update(fees_from_req)
        for fees_alias, fees_value in fees_from_req.items():
            self._set_to_state(FeesStaticHelper.build_path_for_set_fees(alias=fees_alias), fees_value)
        self._set_to_state(FeesStaticHelper.build_path_for_set_fees(), current_fees)

    def _set_to_state(self, key, val):
        val = config_state_serializer.serialize(val)
        key = key.encode()
        self.state.set(key, val)
