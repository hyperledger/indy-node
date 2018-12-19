from binascii import hexlify

from indy_common.state import domain

from indy_common.roles import Roles

from indy_common.constants import NYM

from indy_common.auth import Authoriser
from plenum.common.constants import ROLE, TARGET_NYM, DOMAIN_LEDGER_ID, TRUSTEE, VERKEY, TXN_TIME

from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_from, get_seq_no, get_txn_time
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.nym_handler import NymHandler as PNymHandler


class NymHandler(PNymHandler):

    def __init__(self, config, database_manager: DatabaseManager):
        super().__init__(config, database_manager)

    def static_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        role = operation.get(ROLE)
        nym = operation.get(TARGET_NYM)
        if not nym:
            raise InvalidClientRequest(identifier, req_id,
                                       "{} needs to be present".
                                       format(TARGET_NYM))
        if not Authoriser.isValidRole(role):
            raise InvalidClientRequest(identifier, req_id,
                                       "{} not a valid role".
                                       format(role))

    def dynamic_validation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        try:
            originRole = self.idrCache.getRole(
                identifier, isCommitted=False) or None
        except BaseException:
            raise UnknownIdentifier(
                identifier,
                req_id)

        nymData = self.idrCache.getNym(operation[TARGET_NYM], isCommitted=False)
        if not nymData:
            # If nym does not exist
            self._validateNewNym(request, operation, originRole)
        else:
            self._validateExistingNym(request, operation, originRole, nymData)

    def gen_txn_path(self, txn):
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = domain.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False):
        txn_data = get_payload_data(txn)
        nym = txn_data.get(TARGET_NYM)
        data = {
            f.IDENTIFIER.nm: get_from(txn),
            f.SEQ_NO.nm: get_seq_no(txn),
            TXN_TIME: get_txn_time(txn)
        }
        if ROLE in txn_data:
            data[ROLE] = txn_data.get(ROLE)
        if VERKEY in txn_data:
            data[VERKEY] = txn_data.get(VERKEY)
        self.updateNym(nym, txn, isCommitted=isCommitted)

    def updateNym(self, nym, txn, isCommitted=True):
        updatedData = super().updateNym(nym, txn, isCommitted=isCommitted)
        txn_time = get_txn_time(txn)
        self.idrCache.set(nym,
                          seqNo=get_seq_no(txn),
                          txnTime=txn_time,
                          ta=updatedData.get(f.IDENTIFIER.nm),
                          role=updatedData.get(ROLE),
                          verkey=updatedData.get(VERKEY),
                          isCommitted=isCommitted)

    def _validateNewNym(self, req: Request, op, originRole):
        role = op.get(ROLE)
        r, msg = Authoriser.authorised(NYM,
                                       originRole,
                                       field=ROLE,
                                       oldVal=None,
                                       newVal=role)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "{} cannot add {}".format(
                    Roles.nameFromValue(originRole),
                    Roles.nameFromValue(role))
            )

    def _validateExistingNym(self, req: Request, op, originRole, nymData):
        unauthorized = False
        reason = None
        origin = req.identifier
        owner = self.idrCache.getOwnerFor(op[TARGET_NYM], isCommitted=False)
        isOwner = origin == owner

        if not originRole == TRUSTEE and not isOwner:
            reason = '{} is neither Trustee nor owner of {}' \
                .format(origin, op[TARGET_NYM])
            unauthorized = True

        if not unauthorized:
            updateKeys = [ROLE, VERKEY]
            for key in updateKeys:
                if key in op:
                    newVal = op[key]
                    oldVal = nymData.get(key)
                    if oldVal != newVal:
                        r, msg = Authoriser.authorised(NYM, originRole, field=key,
                                                       oldVal=oldVal, newVal=newVal,
                                                       isActorOwnerOfSubject=isOwner)
                        if not r:
                            unauthorized = True
                            reason = "{} cannot update {}". \
                                format(Roles.nameFromValue(originRole), key)
                            break
        if unauthorized:
            raise UnauthorizedClientRequest(
                req.identifier, req.reqId, reason)

    @property
    def idrCache(self):
        return self.database_manager.get_store('idr')
