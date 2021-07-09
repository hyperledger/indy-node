from typing import Optional

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.req_utils import get_txn_claim_def_schema_ref, get_txn_claim_def_tag, get_txn_claim_def_signature_type, \
    get_txn_claim_def_public_keys, get_write_claim_def_signature_type, get_write_claim_def_schema_ref, \
    get_write_claim_def_tag

from indy_common.constants import CLAIM_DEF, REF, SCHEMA, CLAIM_DEF_PUBLIC_KEYS, CLAIM_DEF_SCHEMA_REF
from indy_common.state.state_constants import MARKER_CLAIM_DEF

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_from, get_seq_no, get_txn_time

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value


class ClaimDefHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, CLAIM_DEF, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        pass

    def additional_dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        # we can not add a Claim Def with existent ISSUER_DID
        # sine a Claim Def needs to be identified by seqNo
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        ref = operation[REF]
        try:
            txn = self.ledger.get_by_seq_no_uncommitted(ref)
        except KeyError:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "Mentioned seqNo ({}) doesn't exist.".format(ref))
        if txn['txn']['type'] != SCHEMA:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "Mentioned seqNo ({}) isn't seqNo of the schema.".format(ref))
        signature_type = get_write_claim_def_signature_type(request)
        schema_ref = get_write_claim_def_schema_ref(request)
        tag = get_write_claim_def_tag(request)

        path = self.make_state_path_for_claim_def(identifier, schema_ref, signature_type, tag)

        claim_def, _, _ = self.get_from_state(path, is_committed=False)

        if claim_def:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=CLAIM_DEF,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=CLAIM_DEF,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = self.prepare_claim_def_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = self.prepare_claim_def_for_state(txn)
        self.state.set(path, value_bytes)
        return txn

    @staticmethod
    def prepare_claim_def_for_state(txn, path_only=False):
        origin = get_from(txn)
        schema_seq_no = get_txn_claim_def_schema_ref(txn)
        if schema_seq_no is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain schema seq no".format(CLAIM_DEF_SCHEMA_REF))
        data = get_txn_claim_def_public_keys(txn)
        if data is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain components of keys"
                             .format(CLAIM_DEF_PUBLIC_KEYS))
        signature_type = get_txn_claim_def_signature_type(txn)
        tag = get_txn_claim_def_tag(txn)
        path = ClaimDefHandler.make_state_path_for_claim_def(origin, schema_seq_no, signature_type, tag)
        if path_only:
            return path
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        value_bytes = encode_state_value(data, seq_no, txn_time)
        return path, value_bytes

    @staticmethod
    def make_state_path_for_claim_def(authors_did, schema_seq_no, signature_type, tag) -> bytes:
        return "{DID}:{MARKER}:{SIGNATURE_TYPE}:{SCHEMA_SEQ_NO}:{TAG}" \
            .format(DID=authors_did,
                    MARKER=MARKER_CLAIM_DEF,
                    SIGNATURE_TYPE=signature_type,
                    SCHEMA_SEQ_NO=schema_seq_no,
                    TAG=tag).encode()
