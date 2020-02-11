from indy_common.constants import GET_RS_MAPPING, RS_META, RS_META_NAME, RS_META_VERSION, RS_MAPPING_FROM, \
    DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetRsMappingHandler(ReadRequestHandler):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_RS_MAPPING, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        author_did = request.operation[RS_MAPPING_FROM]
        name = request.operation[RS_META][RS_META_NAME]
        version = request.operation[RS_META][RS_META_VERSION]
        state_path = GetRsMappingHandler.make_state_path(author_did, name, version)

        rs_encoding, last_seq_no, last_update_time, proof = {}, None, None, None
        try:  # lookup returns: keys, seq_no, last_update_time, proof
            rs_encoding, last_seq_no, last_update_time, proof = self.lookup(state_path, True, True)
        except KeyError:
            pass
        return self.make_result(request=request, data=rs_encoding, last_seq_no=last_seq_no,
                                update_time=last_update_time, proof=proof)
