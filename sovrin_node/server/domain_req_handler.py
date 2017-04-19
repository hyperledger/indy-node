import json
from binascii import unhexlify
from typing import List
from hashlib import sha256

from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest, UnknownIdentifier
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, \
    VERKEY, DATA, NAME, VERSION
from plenum.common.types import f
from plenum.common.util import check_endpoint_valid
from plenum.server.domain_req_handler import DomainRequestHandler as PHandler
from sovrin_common.auth import Authoriser
from sovrin_common.constants import NYM, ROLE, ATTRIB, ENDPOINT, SCHEMA, \
    CLAIM_DEF, REF, SIGNATURE_TYPE
from sovrin_common.types import Request
from stp_core.common.log import getlogger
from stp_core.network.exceptions import EndpointException


logger = getlogger()


class DomainReqHandler(PHandler):
    MARKER_ATTR = "\01"
    MARKER_SCHEMA = "\02"
    MARKER_IPK = "\03"
    LAST_SEQ_NO = "lsn"
    VALUE = "val"

    def __init__(self, ledger, state, requestProcessor, idrCache, attributeStore):
        super().__init__(ledger, state, requestProcessor)
        self.idrCache = idrCache
        self.attributeStore = attributeStore

    def onBatchCreated(self, stateRoot):
        self.idrCache.currentBatchCreated(stateRoot)

    def onBatchRejected(self, stateRoot=None):
        self.idrCache.batchRejected(stateRoot)

    def updateState(self, txns, isCommitted=False):
        for txn in txns:
            typ = txn.get(TXN_TYPE)
            nym = txn.get(TARGET_NYM)
            if typ == NYM:
                data = {f.IDENTIFIER.nm: txn.get(f.IDENTIFIER.nm)}
                if ROLE in txn:
                    data[ROLE] = txn.get(ROLE)
                if VERKEY in txn:
                    data[VERKEY] = txn.get(VERKEY)
                self.updateNym(nym, data, isCommitted=isCommitted)
            elif typ == ATTRIB:
                self._addAttr(txn)
            elif typ == SCHEMA:
                self._addSchema(txn)
            elif typ == CLAIM_DEF:
                self._addClaimDef(txn)
            else:
                logger.debug('Cannot apply request of type {} to state'.format(typ))

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
                raise UnknownIdentifier(
                    req.identifier,
                    req.reqId)

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
                owner = s.getOwnerFor(op[TARGET_NYM], isCommitted=False)
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
            if op.get(TARGET_NYM) and op[TARGET_NYM] != req.identifier and \
                    not s.getOwnerFor(op[TARGET_NYM], isCommitted=False) == origin:
                raise UnauthorizedClientRequest(
                    req.identifier,
                    req.reqId,
                    "Only identity owner/guardian can add attribute "
                    "for that identity")

    def updateNym(self, nym, data, isCommitted=True):
        updatedData = super().updateNym(nym, data, isCommitted=isCommitted)
        self.idrCache.set(nym, ta=updatedData.get(f.IDENTIFIER.nm),
                          verkey=updatedData.get(VERKEY),
                          role=updatedData.get(ROLE),
                          isCommitted=isCommitted)

    def hasNym(self, nym, isCommitted: bool = True):
        return self.idrCache.hasNym(nym, isCommitted=isCommitted)

    def handleGetNymReq(self, request: Request, frm: str):
        nym = request.operation[TARGET_NYM]
        nymData = self.idrCache.getNym(nym, isCommitted=True)
        if nymData:
            nymData[TARGET_NYM] = nym
            data = self.stateSerializer.serialize(nymData)
        else:
            data = None
        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId, DATA: data}
        result.update(request.operation)
        return result

    def lookup(self, path, isCommitted=True) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :return: data
        """
        assert path is not None
        raw = self.state.get(path, isCommitted)
        if raw is None:
            return None, None
        raw = self.stateSerializer.deserialize(raw)
        value = raw.get(self.VALUE)
        lastSeqNo = raw.get(self.LAST_SEQ_NO)
        return value, lastSeqNo

    def _addAttr(self, txn) -> None:
        assert txn[TXN_TYPE] == ATTRIB
        nym = txn.get(TARGET_NYM)

        def parse(txn):
            raw = txn.get(RAW)
            if raw:
                data = json.loads(raw)
                key, value = data.popitem()
                return key, value
            encOrHash = txn.get(ENC) or txn.get(HASH)
            if encOrHash:
                return encOrHash, encOrHash
            raise ValueError("One of 'raw', 'enc', 'hash' "
                             "fields of ATTR must present")

        attrName, value = parse(txn)
        path = self._makeAttrPath(nym, attrName)
        seqNo = txn[f.SEQ_NO.nm]
        value = self.stateSerializer.serialize(value)
        hashedVal = self._hashOf(value)
        valueBytes = self._encodeValue(hashedVal, seqNo)
        self.state.set(path, valueBytes)
        self.attributeStore.set(hashedVal, value)

    def _addSchema(self, txn) -> None:
        assert txn[TXN_TYPE] == SCHEMA
        origin = txn.get(f.IDENTIFIER.nm)

        data = txn.get(DATA)
        schemaName = data[NAME]
        schemaVersion = data[VERSION]
        path = self._makeSchemaPath(origin, schemaName, schemaVersion)

        seqNo = txn[f.SEQ_NO.nm]
        valueBytes = self._encodeValue(data, seqNo)
        self.state.set(path, valueBytes)

    def _addClaimDef(self, txn) -> None:
        assert txn[TXN_TYPE] == CLAIM_DEF
        origin = txn.get(f.IDENTIFIER.nm)

        schemaSeqNo = txn[REF]
        if schemaSeqNo is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain schema seq no".format(REF))
        keys = txn[DATA]
        if keys is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain components of keys"
                             .format(DATA))

        signatureType = txn[SIGNATURE_TYPE]
        path = self._makeClaimDefPath(origin, schemaSeqNo)
        seqNo = txn[f.SEQ_NO.nm]
        values = {
            "keys": keys,
            "signatureType": signatureType
        }
        valueBytes = self._encodeValue(values, seqNo)
        self.state.set(path, valueBytes)

    def getAttr(self,
                did: str,
                key: str,
                isCommitted=True) -> (str, int):
        assert did is not None
        assert key is not None
        path = self._makeAttrPath(did, key)
        hashedVal, lastSeqNo = self.lookup(path, isCommitted)
        try:
            value = self.attributeStore.get(hashedVal)
            value = self.stateSerializer.deserialize(value)
        except KeyError:
            value = hashedVal
        return value, lastSeqNo

    def getSchema(self,
                  author: str,
                  schemaName: str,
                  schemaVersion: str,
                  isCommitted=True) -> (str, int):
        assert author is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = self._makeSchemaPath(author, schemaName, schemaVersion)
        return self.lookup(path, isCommitted)

    def getClaimDef(self,
                    author: str,
                    schemaSeqNo: str,
                    isCommitted=True) -> (str, int):
        assert author is not None
        assert schemaSeqNo is not None
        path = self._makeClaimDefPath(author, schemaSeqNo)
        values, seqno  = self.lookup(path, isCommitted)
        signatureType = values['signatureType']
        keys = values['keys']
        return keys, signatureType, seqno

    @staticmethod
    def _hashOf(text) -> str:
        if not isinstance(text, (str, bytes)):
            text = DomainReqHandler.stateSerializer.serialize(text)
        if not isinstance(text, bytes):
            text = text.encode()
        return sha256(text).hexdigest()

    @staticmethod
    def _makeAttrPath(did, attrName) -> bytes:
        nameHash = DomainReqHandler._hashOf(attrName)
        return "{DID}:{MARKER}:{ATTR_NAME}" \
            .format(DID=did,
                    MARKER=DomainReqHandler.MARKER_ATTR,
                    ATTR_NAME=nameHash).encode()

    @staticmethod
    def _makeSchemaPath(did, schemaName, schemaVersion) -> bytes:
        return "{DID}:{MARKER}:{SCHEMA_NAME}{SCHEMA_VERSION}" \
            .format(DID=did,
                    MARKER=DomainReqHandler.MARKER_SCHEMA,
                    SCHEMA_NAME=schemaName,
                    SCHEMA_VERSION=schemaVersion) \
            .encode()

    @staticmethod
    def _makeClaimDefPath(did, schemaSeqNo) -> bytes:
        return "{DID}:{MARKER}:{SCHEMA_SEQ_NO}" \
                   .format(DID=did,
                           MARKER=DomainReqHandler.MARKER_IPK,
                           SCHEMA_SEQ_NO=schemaSeqNo)\
                   .encode()

    def _encodeValue(self, value, seqNo):
        return self.stateSerializer.serialize({
            DomainReqHandler.LAST_SEQ_NO: seqNo,
            DomainReqHandler.VALUE: value
        })
