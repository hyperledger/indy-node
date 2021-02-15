from indy_common.constants import GET_FEES
from indy_node.server.request_handlers.config_req_handlers.fees.fees_static_helper import FeesStaticHelper
from plenum.common.constants import STATE_PROOF, CONFIG_LEDGER_ID, BLS_LABEL
from plenum.common.request import Request
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetFeesHandler(ReadRequestHandler):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, GET_FEES, CONFIG_LEDGER_ID)

    def get_result(self, request: Request):
        fees, proof = self.get_fees(is_committed=True, with_proof=True)

        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId,
                  f.FEES.nm: fees}
        if proof:
            result[STATE_PROOF] = proof
        result.update(request.operation)
        return result

    def get_fees(self, is_committed=False, with_proof=False):
        result = FeesStaticHelper.get_fee_from_state(self.state, is_committed=is_committed, with_proof=with_proof,
                                                     bls_store=self.database_manager.get_store(BLS_LABEL))
        if with_proof:
            fees, proof = result
            return (fees, proof) if fees is not None else ({}, proof)
        else:
            return result if result is not None else {}
