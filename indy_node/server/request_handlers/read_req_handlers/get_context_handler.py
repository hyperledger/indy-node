from indy_common.constants import GET_CONTEXT
from indy_common.req_utils import get_read_context_from, get_read_context_name, get_read_context_version
from indy_node.server.request_handlers.domain_req_handlers.context_handler import ContextHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetContextHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_CONTEXT, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        author_did = get_read_context_from(request)
        context_name = get_read_context_name(request)
        context_version = get_read_context_version(request)
        context, last_seq_no, last_update_time, proof = self.get_context(
            author=author_did,
            context_name=context_name,
            context_version=context_version,
            with_proof=True
        )
        return self.make_result(request=request,
                                data=context,
                                last_seq_no=last_seq_no,
                                update_time=last_update_time,
                                proof=proof)

    def get_context(self,
                    author: str,
                    context_name: str,
                    context_version: str,
                    is_committed=True,
                    with_proof=True) -> (str, int, int, list):
        assert author is not None
        assert context_name is not None
        assert context_version is not None
        path = ContextHandler.make_state_path_for_context(author, context_name, context_version)
        try:
            keys, seq_no, last_update_time, proof = self.lookup(path, is_committed, with_proof=with_proof)
            return keys, seq_no, last_update_time, proof
        except KeyError:
            return None, None, None, None
