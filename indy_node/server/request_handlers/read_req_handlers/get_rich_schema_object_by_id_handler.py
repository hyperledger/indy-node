from indy_common.constants import GET_RICH_SCHEMA_OBJECT_BY_ID, RS_ID
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetRichSchemaObjectByIdHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_RICH_SCHEMA_OBJECT_BY_ID, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        id = request.operation[RS_ID]

        try:
            value, seq_no, last_update_time, proof = self.lookup(id, is_committed=True, with_proof=True)
        except KeyError:
            value, seq_no, last_update_time, proof = None, None, None, None

        return self.make_result(request=request,
                                data=value,
                                last_seq_no=seq_no,
                                update_time=last_update_time,
                                proof=proof)
