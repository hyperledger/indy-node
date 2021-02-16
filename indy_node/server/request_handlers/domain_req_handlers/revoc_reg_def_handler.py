from typing import Optional

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import REVOC_REG_DEF, CRED_DEF_ID, REVOC_TYPE, TAG, ISSUANCE_BY_DEFAULT, ISSUANCE_ON_DEMAND
from indy_common.state.state_constants import MARKER_REVOC_DEF
from indy_node.server.revocation_strategy import RevokedStrategy, IssuedStrategy
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_seq_no, get_txn_time, get_from, get_payload_data

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class RevocRegDefHandler(WriteRequestHandler):
    revocation_strategy_map = {
        ISSUANCE_BY_DEFAULT: RevokedStrategy,
        ISSUANCE_ON_DEMAND: IssuedStrategy,
    }

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, REVOC_REG_DEF, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    @staticmethod
    def get_revocation_strategy(typ):
        return RevocRegDefHandler.revocation_strategy_map.get(typ)

    def static_validation(self, request: Request):
        cred_def_id = request.operation.get(CRED_DEF_ID)
        tags = cred_def_id.split(":")
        if len(tags) != 4 and len(tags) != 5:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "Format of {} field is not acceptable. "
                                       "Expected: 'did:marker:signature_type:schema_ref' or "
                                       "'did:marker:signature_type:schema_ref:tag'".format(CRED_DEF_ID))

    def additional_dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)
        operation = request.operation
        cred_def_id = operation.get(CRED_DEF_ID)
        revoc_def_type = operation.get(REVOC_TYPE)
        revoc_def_tag = operation.get(TAG)
        assert cred_def_id
        assert revoc_def_tag
        assert revoc_def_type

        revoc_def_id = RevocRegDefHandler.make_state_path_for_revoc_def(request.identifier,
                                                                        cred_def_id,
                                                                        revoc_def_type,
                                                                        revoc_def_tag)
        revoc_def, _, _ = self.get_from_state(revoc_def_id)

        if revoc_def is None:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=REVOC_REG_DEF,
                                                             field='*',
                                                             value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=REVOC_REG_DEF,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])

        cred_def, _, _ = self.get_from_state(cred_def_id)
        if cred_def is None:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       "There is no any CRED_DEF by path: {}".format(cred_def_id))

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = RevocRegDefHandler.prepare_revoc_def_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False):
        self._validate_txn_type(txn)
        path, value_bytes = RevocRegDefHandler.prepare_revoc_def_for_state(txn)
        self.state.set(path, value_bytes)
        return txn

    @staticmethod
    def prepare_revoc_def_for_state(txn, path_only=False):
        author_did = get_from(txn)
        txn_data = get_payload_data(txn)
        cred_def_id = txn_data.get(CRED_DEF_ID)
        revoc_def_type = txn_data.get(REVOC_TYPE)
        revoc_def_tag = txn_data.get(TAG)
        assert author_did
        assert cred_def_id
        assert revoc_def_type
        assert revoc_def_tag
        path = RevocRegDefHandler.make_state_path_for_revoc_def(author_did,
                                                                cred_def_id,
                                                                revoc_def_type,
                                                                revoc_def_tag)
        if path_only:
            return path
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        assert seq_no
        assert txn_time
        value_bytes = encode_state_value(txn_data, seq_no, txn_time)
        return path, value_bytes

    @staticmethod
    def make_state_path_for_revoc_def(authors_did, cred_def_id, revoc_def_type, revoc_def_tag) -> bytes:
        return "{DID}:{MARKER}:{CRED_DEF_ID}:{REVOC_DEF_TYPE}:{REVOC_DEF_TAG}" \
            .format(DID=authors_did,
                    MARKER=MARKER_REVOC_DEF,
                    CRED_DEF_ID=cred_def_id,
                    REVOC_DEF_TYPE=revoc_def_type,
                    REVOC_DEF_TAG=revoc_def_tag).encode()
