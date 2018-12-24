from indy_common.state import domain

from indy_node.server.request_handlers.read_request_handler import ReadRequestHandler
from plenum.common.exceptions import InvalidClientRequest


class GetRevocRegHandler(ReadRequestHandler):
    def _get_current_revoc_entry_and_revoc_def(self, author_did, revoc_reg_def_id, req_id):
        assert revoc_reg_def_id
        current_entry, _, _, _ = self.getRevocDefEntry(revoc_reg_def_id=revoc_reg_def_id,
                                                       isCommitted=False)
        revoc_def, _, _, _ = self.lookup(revoc_reg_def_id, isCommitted=False, with_proof=False)
        if revoc_def is None:
            raise InvalidClientRequest(author_did,
                                       req_id,
                                       "There is no any REVOC_REG_DEF by path: {}".format(revoc_reg_def_id))
        return current_entry, revoc_def

    def getRevocDefEntry(self,
                         revoc_reg_def_id,
                         isCommitted=True) -> (str, int, int, list):
        assert revoc_reg_def_id
        path = domain.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=False)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None
