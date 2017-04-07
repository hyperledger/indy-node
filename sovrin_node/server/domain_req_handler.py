import json
from binascii import unhexlify
from typing import List

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, VERKEY, \
    GUARDIAN, DATA, STEWARD
from plenum.common.txn_util import reqToTxn
from plenum.common.types import f, RequestAck, Reply
from plenum.common.util import check_endpoint_valid
from plenum.server.domain_req_handler import DomainRequestHandler as PHandler
from sovrin_common.auth import Authoriser
from sovrin_common.constants import NYM, ROLE, ATTRIB, ENDPOINT
from sovrin_common.types import Request
from stp_core.network.exceptions import EndpointException


class DomainReqHandler(PHandler):
    def __init__(self, ledger, state, idrCache, requestProcessor):
        super().__init__(ledger, state, requestProcessor)
        self.idrCache = idrCache

    def onBatchCreated(self, stateRoot):
        self.idrCache.currentBatchCreated(stateRoot)

    def commit(self, txnCount, stateRoot, txnRoot) -> List:
        r = super().commit(txnCount, stateRoot, txnRoot)
        self.idrCache.onBatchCommitted(unhexlify(stateRoot.encode()))
        return r

    def canNymRequestBeProcessed(self, identifier, msg) -> (bool, str):
        nym = msg.get(TARGET_NYM)
        if self.hasNym(nym, isCommitted=False):
            if not self.idrCache.hasTrustee(identifier, isCommitted=False) and \
                            self.idrCache.getOwnerFor(nym, isCommitted=False) != identifier:
                reason = '{} is neither Trustee nor owner of {}'\
                    .format(identifier, nym)
                return False, reason
        return True, ''

    def doStaticValidation(self, identifier, reqId, operation):
        if operation[TXN_TYPE] == NYM:
            role = operation.get(ROLE)
            nym = operation.get(TARGET_NYM)
            if not nym:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} needs to be present".
                                           format(TARGET_NYM))
            if not Authoriser.isValidRole(role):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid role".
                                           format(role))
            s, reason = self.canNymRequestBeProcessed(identifier, operation)
            if not s:
                raise InvalidClientRequest(identifier, reqId, reason)

        if operation[TXN_TYPE] == ATTRIB:
            dataKeys = {RAW, ENC, HASH}.intersection(set(operation.keys()))
            if len(dataKeys) != 1:
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should have one and only one of '
                                           '{}, {}, {}'
                                           .format(ATTRIB, RAW, ENC, HASH))
            if RAW in dataKeys:
                try:
                    data = json.loads(operation[RAW])
                    endpoint = data.get(ENDPOINT, {}).get('ha')
                    check_endpoint_valid(endpoint, required=False)

                except EndpointException as exc:
                    raise InvalidClientRequest(identifier, reqId, str(exc))
                except BaseException as exc:
                    raise InvalidClientRequest(identifier, reqId, str(exc))
                    # PREVIOUS CODE, ASSUMED ANY EXCEPTION WAS A JSON ISSUE
                    # except:
                    #     raise InvalidClientRequest(identifier, reqId,
                    #                                'raw attribute {} should be '
                    #                                'JSON'.format(operation[RAW]))

            if not (not operation.get(TARGET_NYM) or
                    self.hasNym(operation[TARGET_NYM], isCommitted=False)):
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should be added before adding '
                                           'attribute for it'.
                                           format(TARGET_NYM))

    def validate(self, req: Request, config=None):
        op = req.operation
        typ = op[TXN_TYPE]

        s = self.idrCache

        origin = req.identifier

        if typ == NYM:
            try:
                originRole = s.getRole(origin, isCommitted=False) or None
            except:
                raise UnauthorizedClientRequest(
                    req.identifier,
                    req.reqId,
                    "Nym {} not added to the ledger yet".format(origin))

            nymData = s.getNym(op[TARGET_NYM], isCommitted=False)
            if not nymData:
                # If nym does not exist
                role = op.get(ROLE)
                r, msg = Authoriser.authorised(NYM, ROLE, originRole,
                                               oldVal=None, newVal=role)
                if not r:
                    raise UnauthorizedClientRequest(
                        req.identifier,
                        req.reqId,
                        "{} cannot add {}".format(originRole, role))
            else:
                owner = s.getOwnerFor(op[TARGET_NYM])
                isOwner = origin == owner
                updateKeys = [ROLE, VERKEY]
                for key in updateKeys:
                    if key in op:
                        newVal = op[key]
                        oldVal = nymData.get(key)
                        if oldVal != newVal:
                            r, msg = Authoriser.authorised(NYM, key, originRole,
                                                           oldVal=oldVal,
                                                           newVal=newVal,
                                                           isActorOwnerOfSubject=isOwner)
                            if not r:
                                raise UnauthorizedClientRequest(
                                    req.identifier,
                                    req.reqId,
                                    "{} cannot update {}".format(originRole,
                                                                 key))

        elif typ == ATTRIB:
            if op.get(TARGET_NYM) and \
                            op[TARGET_NYM] != req.identifier and \
                    not s.getOwnerFor(op[TARGET_NYM]) == origin:
                raise UnauthorizedClientRequest(
                    req.identifier,
                    req.reqId,
                    "Only identity owner/guardian can add attribute "
                    "for that identity")

    def updateNym(self, nym, data, isCommitted=True):
        updatedData = super().updateNym(nym, data, isCommitted=isCommitted)
        self.idrCache.set(nym, ta=updatedData.get(f.IDENTIFIER.nm),
                          verkey=data.get(VERKEY),
                          role=data.get(ROLE),
                          isCommitted=isCommitted)

    def hasNym(self, nym, isCommitted: bool = True):
        return self.idrCache.hasNym(nym, isCommitted=isCommitted)

    def handleGetNymReq(self, request: Request, frm: str):
        nym = request.operation[TARGET_NYM]
        nymData = self.idrCache.getNym(nym, isCommitted=True)
        # TODO: We should have a single JSON encoder which does the
        # encoding for us, like sorting by keys, handling datetime objects.
        if nymData:
            nymData[TARGET_NYM] = nym
            data = json.dumps(nymData, sort_keys=True)
        else:
            data = None
        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId, DATA: data}
        result.update(request.operation)
        return result
