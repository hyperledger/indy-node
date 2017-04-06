import json

from plenum.common.exceptions import InvalidClientRequest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, VERKEY
from plenum.common.txn_util import reqToTxn
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

    def updateState(self, txns, isCommitted=False):
        for txn in txns:
            typ = txn.get(TXN_TYPE)
            nym = txn.get(TARGET_NYM)
            if typ == NYM:
                self.updateNym(nym, {
                    ROLE: txn.get(ROLE),
                    VERKEY: txn.get(VERKEY)
                }, isCommitted=isCommitted)

    def updateNym(self, nym, data, isCommitted=True):
        existingData = self.getNymDetails(self.state, nym,
                                          isCommitted=isCommitted)
        existingData.update(data)
        key = nym.encode()
        val = self.stateSerializer.serialize(data)
        self.state.set(key, val)

    def hasNym(self, nym, isCommitted: bool = True):
        return self.idrCache.hasNym(nym, isCommitted=isCommitted)

    def onBatchCreated(self, seqNo):
        pass