from indy_common.state import domain

from indy_common.constants import CLAIM_DEF_SIGNATURE_TYPE, GET_CLAIM_DEF
from indy_common.req_utils import get_read_claim_def_from, get_read_claim_def_signature_type, \
    get_read_claim_def_schema_ref, get_read_claim_def_tag

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetClaimDefHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_CLAIM_DEF, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        frm = get_read_claim_def_from(request)
        signature_type = get_read_claim_def_signature_type(request)
        schema_ref = get_read_claim_def_schema_ref(request)
        tag = get_read_claim_def_tag(request)
        keys, last_seq_no, last_update_time, proof = self.get_claim_def(
            author=frm,
            schema_seq_no=schema_ref,
            signature_type=signature_type,
            tag=tag
        )
        result = self.make_result(request=request,
                                  data=keys,
                                  last_seq_no=last_seq_no,
                                  update_time=last_update_time,
                                  proof=proof)
        result[CLAIM_DEF_SIGNATURE_TYPE] = signature_type
        return result

    def get_claim_def(self,
                      author: str,
                      schema_seq_no: str,
                      signature_type,
                      tag,
                      is_committed=True) -> (str, int, int, list):
        assert author is not None
        assert schema_seq_no is not None
        path = domain.make_state_path_for_claim_def(author, schema_seq_no, signature_type, tag)
        try:
            keys, seq_no, last_update_time, proof = self.lookup(path, is_committed, with_proof=True)
            return keys, seq_no, last_update_time, proof
        except KeyError:
            return None, None, None, None
