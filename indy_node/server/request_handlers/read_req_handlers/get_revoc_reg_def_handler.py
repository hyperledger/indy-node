from indy_common.constants import ID, GET_REVOC_REG_DEF

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetRevocRegDefHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_REVOC_REG_DEF, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        state_path = request.operation.get(ID, None)
        assert state_path
        try:
            keys, last_seq_no, last_update_time, proof = self.lookup(state_path, is_committed=True, with_proof=True)
        except KeyError:
            keys, last_seq_no, last_update_time, proof = None, None, None, None
        result = self.make_result(request=request,
                                  data=keys,
                                  last_seq_no=last_seq_no,
                                  update_time=last_update_time,
                                  proof=proof)
        return result
