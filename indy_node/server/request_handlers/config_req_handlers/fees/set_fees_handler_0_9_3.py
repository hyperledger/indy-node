from indy_common.constants import FEES
from indy_node.server.request_handlers.config_req_handlers.fees.fees_static_helper import FeesStaticHelper
from indy_node.server.request_handlers.config_req_handlers.fees.set_fees_handler import SetFeesHandler
from plenum.common.txn_util import get_payload_data
from plenum.common.types import f


class SetFeesHandler093(SetFeesHandler):
    fees_state_key = 'fees'

    def update_state(self, txn, prev_result, request, is_committed=False):
        payload = get_payload_data(txn)
        fees_from_req = payload.get(FEES)
        current_fees = FeesStaticHelper.get_fee_from_state(self.state)
        current_fees = current_fees if current_fees else {}
        current_fees.update(fees_from_req)
        self._set_to_state(self.fees_state_key, current_fees)
