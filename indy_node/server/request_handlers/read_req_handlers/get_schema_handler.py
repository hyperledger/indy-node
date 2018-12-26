from indy_common.state import domain

from indy_node.server.request_handlers.read_request_handler import ReadRequestHandler


class GetSchemaHandler(ReadRequestHandler):

    def get_schema(self,
                   author: str,
                   schemaName: str,
                   schemaVersion: str,
                   isCommitted=True,
                   with_proof=True) -> (str, int, int, list):
        assert author is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = domain.make_state_path_for_schema(author, schemaName, schemaVersion)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=with_proof)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None
