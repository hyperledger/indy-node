from indy_common.auth import Authoriser

from indy_common.state import domain

from indy_common.constants import CLAIM_DEF, REF, SCHEMA

from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import UnauthorizedClientRequest, UnknownIdentifier, InvalidClientRequest
from plenum.common.request import Request
from plenum.common.roles import Roles
from plenum.common.txn_util import get_type
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class ClaimDefHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, CLAIM_DEF, DOMAIN_LEDGER_ID)

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        # we can not add a Claim Def with existent ISSUER_DID
        # sine a Claim Def needs to be identified by seqNo
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
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
        try:
            origin_role = self.idrCache.getRole(
                identifier, isCommitted=False) or None
        except BaseException:
            raise UnknownIdentifier(
                identifier,
                req_id)
        # only owner can update claim_def,
        # because his identifier is the primary key of claim_def
        r, msg = Authoriser.authorised(typ=CLAIM_DEF,
                                       actorRole=origin_role,
                                       isActorOwnerOfSubject=True)
        if not r:
            raise UnauthorizedClientRequest(
                identifier,
                req_id,
                "{} cannot add claim def".format(
                    Roles.nameFromValue(origin_role)
                    if origin_role else "Person without role")
            )

    def gen_txn_path(self, txn):
        path = domain.prepare_claim_def_for_state(txn, path_only=True)
        return path.decode()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False) -> None:
        assert get_type(txn) == CLAIM_DEF
        path, value_bytes = domain.prepare_claim_def_for_state(txn)
        self.state.set(path, value_bytes)

    @property
    def idrCache(self):
        return self.database_manager.get_store('idr')
