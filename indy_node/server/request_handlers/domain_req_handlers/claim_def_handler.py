from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.state import domain

from indy_common.constants import CLAIM_DEF, REF, SCHEMA

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data

from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class ClaimDefHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_request_validator: WriteRequestValidator):
        super().__init__(database_manager, CLAIM_DEF, DOMAIN_LEDGER_ID)
        self.write_request_validator = write_request_validator

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        # we can not add a Claim Def with existent ISSUER_DID
        # sine a Claim Def needs to be identified by seqNo
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        ref = operation[REF]
        try:
            txn = self.ledger.getBySeqNo(ref)
        except KeyError:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "Mentioned seqNo ({}) doesn't exist.".format(ref))
        if txn['txn']['type'] != SCHEMA:
            raise InvalidClientRequest(identifier,
                                       req_id,
                                       "Mentioned seqNo ({}) isn't seqNo of the schema.".format(ref))
        # only owner can update claim_def,
        # because his identifier is the primary key of claim_def
        self.write_request_validator.validate(request,
                                              [AuthActionAdd(txn_type=CLAIM_DEF,
                                                             field='*',
                                                             value='*')])

    def gen_state_key(self, txn):
        self._validate_txn_type(txn)
        path = domain.prepare_claim_def_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, is_committed=True) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = domain.prepare_claim_def_for_state(txn)
        self.state.set(path, value_bytes)
