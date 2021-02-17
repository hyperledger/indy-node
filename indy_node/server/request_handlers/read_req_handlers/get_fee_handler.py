from indy_common.constants import GET_FEE
from indy_node.server.request_handlers.config_req_handlers.fees.fees_static_helper import FeesStaticHelper
from plenum.common.constants import ALIAS, STATE_PROOF, CONFIG_LEDGER_ID, BLS_LABEL
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetFeeHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_FEE, CONFIG_LEDGER_ID)

    def get_result(self, request: Request):
        alias = request.operation.get(ALIAS)
        fee, proof = FeesStaticHelper.get_fee_from_state(self.state, fees_alias=alias, is_committed=True,
                                                         with_proof=True,
                                                         bls_store=self.database_manager.get_store(BLS_LABEL))
        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId, f.FEE.nm: fee}
        if proof:
            result[STATE_PROOF] = proof
        result.update(request.operation)
        return result
