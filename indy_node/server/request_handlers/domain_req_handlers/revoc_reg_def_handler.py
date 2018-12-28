from indy_common.state import domain

from indy_common.constants import REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, TAG
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_def_handler import GetRevocRegDefHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_type, get_request_data

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class RevocRegDefHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager, get_revoc_reg_def: GetRevocRegDefHandler):
        super().__init__(database_manager, REVOC_REG_DEF, DOMAIN_LEDGER_ID)
        self.get_revoc_reg_def = get_revoc_reg_def

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        cred_def_id = operation.get(CRED_DEF_ID)
        revoc_def_type = operation.get(REVOC_TYPE)
        revoc_def_tag = operation.get(TAG)
        assert cred_def_id
        assert revoc_def_tag
        assert revoc_def_type
        tags = cred_def_id.split(":")
        if len(tags) != 4 and len(tags) != 5:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "Format of {} field is not acceptable. "
                                       "Expected: 'did:marker:signature_type:schema_ref' or "
                                       "'did:marker:signature_type:schema_ref:tag'".format(CRED_DEF_ID))
        cred_def, _, _, _ = self.get_revoc_reg_def.lookup(cred_def_id, is_committed=False, with_proof=False)
        if cred_def is None:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "There is no any CRED_DEF by path: {}".format(cred_def_id))

    def gen_state_key(self, txn):
        self._validate_txn_type(txn)
        path = domain.prepare_revoc_def_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, is_committed=False):
        self._validate_txn_type(txn)
        path, value_bytes = domain.prepare_revoc_def_for_state(txn)
        self.state.set(path, value_bytes)
