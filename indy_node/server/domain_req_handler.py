import json
from typing import List
from hashlib import sha256

from copy import deepcopy

import base58
import base64

from common.serializers.serialization import state_roots_serializer
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest, UnknownIdentifier
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, \
    VERKEY, DATA, NAME, VERSION, ORIGIN, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, TXN_TIME
from plenum.common.types import f
from plenum.server.domain_req_handler import DomainRequestHandler as PHandler
from indy_common.auth import Authoriser
from indy_common.constants import NYM, ROLE, ATTRIB, SCHEMA, CLAIM_DEF, REF, \
    SIGNATURE_TYPE
from indy_common.roles import Roles
from indy_common.serialization import attrib_raw_data_serializer
from indy_common.types import Request
from stp_core.common.log import getlogger
from indy_node.persistence.idr_cache import IdrCache

logger = getlogger()


class DomainReqHandler(PHandler):
    MARKER_ATTR = "\01"
    MARKER_SCHEMA = "\02"
    MARKER_CLAIM_DEF = "\03"
    LAST_SEQ_NO = "lsn"
    VALUE = "val"
    LAST_UPDATE_TIME = "lut"

    def __init__(self, ledger, state, requestProcessor,
                 idrCache, attributeStore, bls_store):
        super().__init__(ledger, state, requestProcessor, bls_store)
        self.idrCache = idrCache  # type: IdrCache
        self.attributeStore = attributeStore

    def onBatchCreated(self, stateRoot):
        self.idrCache.currentBatchCreated(stateRoot)

    def onBatchRejected(self):
        self.idrCache.batchRejected()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False):
        typ = txn.get(TXN_TYPE)
        nym = txn.get(TARGET_NYM)
        if typ == NYM:
            data = {
                f.IDENTIFIER.nm: txn.get(f.IDENTIFIER.nm),
                f.SEQ_NO.nm: txn.get(f.SEQ_NO.nm),
                TXN_TIME: txn.get(TXN_TIME)
            }
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
            logger.debug(
                'Cannot apply request of type {} to state'.format(typ))

    def commit(self, txnCount, stateRoot, txnRoot) -> List:
        r = super().commit(txnCount, stateRoot, txnRoot)
        stateRoot = base58.b58decode(stateRoot.encode())
        self.idrCache.onBatchCommitted(stateRoot)
        return r

    def canNymRequestBeProcessed(self, identifier, msg) -> (bool, str):
        nym = msg.get(TARGET_NYM)
        if self.hasNym(nym, isCommitted=False):
            if not self.idrCache.hasTrustee(
                    identifier, isCommitted=False) and self.idrCache.getOwnerFor(
                    nym, isCommitted=False) != identifier:
                reason = '{} is neither Trustee nor owner of {}'\
                    .format(identifier, nym)
                return False, reason
        return True, ''

    def doStaticValidation(self, identifier, reqId, operation):
        if operation[TXN_TYPE] == NYM:
            self._doStaticValidationNym(identifier, reqId, operation)
        if operation[TXN_TYPE] == ATTRIB:
            self._doStaticValidationAttrib(identifier, reqId, operation)

    def _doStaticValidationNym(self, identifier, reqId, operation):
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
        # TODO: This is not static validation as it involves state
        s, reason = self.canNymRequestBeProcessed(identifier, operation)
        if not s:
            raise InvalidClientRequest(identifier, reqId, reason)

    @staticmethod
    def _validate_attrib_keys(operation):
        dataKeys = {RAW, ENC, HASH}.intersection(set(operation.keys()))
        if len(dataKeys) != 1:
            return False
        else:
            return True

    def _doStaticValidationAttrib(self, identifier, reqId, operation):
        if not self._validate_attrib_keys(operation):
            raise InvalidClientRequest(identifier, reqId,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))

        # TODO: This is not static validation as it involves state
        if not (not operation.get(TARGET_NYM) or
                self.hasNym(operation[TARGET_NYM], isCommitted=False)):
            raise InvalidClientRequest(identifier, reqId,
                                       '{} should be added before adding '
                                       'attribute for it'.
                                       format(TARGET_NYM))

    def validate(self, req: Request, config=None):
        op = req.operation
        typ = op[TXN_TYPE]

        if typ == NYM:
            self._validateNym(req)
        elif typ == ATTRIB:
            self._validateAttrib(req)

    def _validateNym(self, req: Request):
        origin = req.identifier
        op = req.operation

        try:
            originRole = self.idrCache.getRole(
                origin, isCommitted=False) or None
        except BaseException:
            raise UnknownIdentifier(
                req.identifier,
                req.reqId)

        nymData = self.idrCache.getNym(op[TARGET_NYM], isCommitted=False)
        if not nymData:
            # If nym does not exist
            self._validateNewNym(req, op, originRole)
        else:
            self._validateExistingNym(req, op, originRole, nymData)

    def _validateNewNym(self, req: Request, op, originRole):
        role = op.get(ROLE)
        r, msg = Authoriser.authorised(NYM, ROLE, originRole,
                                       oldVal=None, newVal=role)
        if not r:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "{} cannot add {}".format(
                    Roles.nameFromValue(originRole),
                    Roles.nameFromValue(role))
            )

    def _validateExistingNym(self, req: Request, op, originRole, nymData):
        origin = req.identifier
        owner = self.idrCache.getOwnerFor(op[TARGET_NYM], isCommitted=False)
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
                            req.identifier, req.reqId, "{} cannot update {}".format(
                                Roles.nameFromValue(originRole), key))

    def _validateAttrib(self, req: Request):
        origin = req.identifier
        op = req.operation
        if op.get(TARGET_NYM) and op[TARGET_NYM] != req.identifier and \
                not self.idrCache.getOwnerFor(op[TARGET_NYM], isCommitted=False) == origin:
            raise UnauthorizedClientRequest(
                req.identifier,
                req.reqId,
                "Only identity owner/guardian can add attribute "
                "for that identity")

    def updateNym(self, nym, data, isCommitted=True):
        updatedData = super().updateNym(nym, data, isCommitted=isCommitted)
        txn_time = data.get(TXN_TIME)
        self.idrCache.set(nym,
                          seqNo=data[f.SEQ_NO.nm],
                          txnTime=txn_time,
                          ta=updatedData.get(f.IDENTIFIER.nm),
                          role=updatedData.get(ROLE),
                          verkey=updatedData.get(VERKEY),
                          isCommitted=isCommitted)

    def hasNym(self, nym, isCommitted: bool = True):
        return self.idrCache.hasNym(nym, isCommitted=isCommitted)

    def handleGetNymReq(self, request: Request, frm: str):
        nym = request.operation[TARGET_NYM]
        nymData = self.idrCache.getNym(nym, isCommitted=True)
        if nymData:
            nymData[TARGET_NYM] = nym
            data = self.stateSerializer.serialize(nymData)
            seq_no = nymData[f.SEQ_NO.nm]
            update_time = nymData[TXN_TIME]
            proof = self.make_proof(self.nym_to_state_key(nym))
        else:
            data = None
            seq_no = None
            proof = None
            update_time = None

        # TODO: add update time here!
        result = self.make_result(request=request,
                                  data=data,
                                  last_seq_no=seq_no,
                                  update_time=update_time,
                                  proof=proof)

        result.update(request.operation)
        return result

    def handleGetSchemaReq(self, request: Request, frm: str):
        authorDid = request.operation[TARGET_NYM]
        schema, lastSeqNo, lastUpdateTime, proof = self.getSchema(
            author=authorDid,
            schemaName=(request.operation[DATA][NAME]),
            schemaVersion=(request.operation[DATA][VERSION])
        )
        return self.make_result(request=request,
                                data=schema,
                                last_seq_no=lastSeqNo,
                                update_time=lastUpdateTime,
                                proof=proof)

    def handleGetClaimDefReq(self, request: Request, frm: str):
        signatureType = request.operation[SIGNATURE_TYPE]
        keys, lastSeqNo, lastUpdateTime, proof = self.getClaimDef(
            author=request.operation[ORIGIN],
            schemaSeqNo=request.operation[REF],
            signatureType=signatureType
        )
        result = self.make_result(request=request,
                                  data=keys,
                                  last_seq_no=lastSeqNo,
                                  update_time=lastUpdateTime,
                                  proof=proof)
        result[SIGNATURE_TYPE] = signatureType
        return result

    def handleGetAttrsReq(self, request: Request, frm: str):
        if not self._validate_attrib_keys(request.operation):
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))
        nym = request.operation[TARGET_NYM]
        if RAW in request.operation:
            attr_key = request.operation[RAW]
        elif ENC in request.operation:
            # If attribute is encrypted, it will be queried by its hash
            attr_key = request.operation[ENC]
        else:
            attr_key = request.operation[HASH]
        value, lastSeqNo, lastUpdateTime, proof = \
            self.getAttr(did=nym, key=attr_key)
        attr = None
        if value is not None:
            if HASH in request.operation:
                attr = attr_key
            else:
                attr = value
        return self.make_result(request=request,
                                data=attr,
                                last_seq_no=lastSeqNo,
                                update_time=lastUpdateTime,
                                proof=proof)

    def make_proof(self, path):
        proof = self.state.generate_state_proof(path, serialize=True)
        root_hash = self.state.committedHeadHash
        # TODO: move to serialization.py
        encoded_proof = base64.b64encode(proof)
        encoded_root_hash = state_roots_serializer.serialize(bytes(root_hash))
        multi_sig = self.bls_store.get(encoded_root_hash)
        return {
            ROOT_HASH: encoded_root_hash,
            MULTI_SIGNATURE: multi_sig,  # [["participants"], "signature", "encoded_pool_root_hash" ]
            PROOF_NODES: encoded_proof
        }

    def lookup(self, path, isCommitted=True) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :return: data
        """
        assert path is not None
        encoded = self.state.get(path, isCommitted)
        if encoded is None:
            raise KeyError
        decoded = self.stateSerializer.deserialize(encoded)
        value = decoded.get(self.VALUE)
        lastSeqNo = decoded.get(self.LAST_SEQ_NO)
        lastUpdateTime = decoded.get(self.LAST_UPDATE_TIME)
        proof = self.make_proof(path)
        return value, lastSeqNo, lastUpdateTime, proof

    def _addAttr(self, txn) -> None:
        """
        The state trie stores the hash of the whole attribute data at:
            the did+attribute name if the data is plaintext (RAW)
            the did+hash(attribute) if the data is encrypted (ENC)
        If the attribute is HASH, then nothing is stored in attribute store,
        the trie stores a blank value for the key did+hash
        """
        assert txn[TXN_TYPE] == ATTRIB
        nym = txn.get(TARGET_NYM)
        attr_key, value = self._parse_attr(txn)
        hashedVal = self._hashOf(value) if value else ''
        seqNo = txn[f.SEQ_NO.nm]
        txnTime = txn[TXN_TIME]
        valueBytes = self._encodeValue(hashedVal, seqNo, txnTime)
        path = self._makeAttrPath(nym, attr_key)
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
        txnTime = txn[TXN_TIME]
        valueBytes = self._encodeValue(data, seqNo, txnTime)
        self.state.set(path, valueBytes)

    def _addClaimDef(self, txn) -> None:
        assert txn[TXN_TYPE] == CLAIM_DEF
        origin = txn.get(f.IDENTIFIER.nm)

        schemaSeqNo = txn.get(REF)
        if schemaSeqNo is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain schema seq no".format(REF))
        data = txn.get(DATA)
        if data is None:
            raise ValueError("'{}' field is absent, "
                             "but it must contain components of keys"
                             .format(DATA))

        signatureType = txn.get(SIGNATURE_TYPE, 'CL')
        path = self._makeClaimDefPath(origin, schemaSeqNo, signatureType)
        seqNo = txn[f.SEQ_NO.nm]
        txnTime = txn[TXN_TIME]
        valueBytes = self._encodeValue(data, seqNo, txnTime)
        self.state.set(path, valueBytes)

    def getAttr(self,
                did: str,
                key: str,
                isCommitted=True) -> (str, int, int, list):
        assert did is not None
        assert key is not None
        path = self._makeAttrPath(did, key)
        try:
            hashed_val, lastSeqNo, lastUpdateTime, proof = \
                self.lookup(path, isCommitted)
        except KeyError:
            return None, None, None, None
        if hashed_val == '':
            # Its a HASH attribute
            return hashed_val, lastSeqNo, lastUpdateTime, proof
        else:
            try:
                value = self.attributeStore.get(hashed_val)
            except KeyError:
                logger.error('Could not get value from attribute store for {}'
                             .format(hashed_val))
                return None, None, None, None
        return value, lastSeqNo, lastUpdateTime, proof

    def getSchema(self,
                  author: str,
                  schemaName: str,
                  schemaVersion: str,
                  isCommitted=True) -> (str, int, int, list):
        assert author is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = self._makeSchemaPath(author, schemaName, schemaVersion)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

    def getClaimDef(self,
                    author: str,
                    schemaSeqNo: str,
                    signatureType='CL',
                    isCommitted=True) -> (str, int, int, list):
        assert author is not None
        assert schemaSeqNo is not None
        path = self._makeClaimDefPath(author, schemaSeqNo, signatureType)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

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
        return "{DID}:{MARKER}:{SCHEMA_NAME}:{SCHEMA_VERSION}" \
            .format(DID=did,
                    MARKER=DomainReqHandler.MARKER_SCHEMA,
                    SCHEMA_NAME=schemaName,
                    SCHEMA_VERSION=schemaVersion) \
            .encode()

    @staticmethod
    def _makeClaimDefPath(did, schemaSeqNo, signatureType) -> bytes:
        return "{DID}:{MARKER}:{SIGNATURE_TYPE}:{SCHEMA_SEQ_NO}" \
            .format(DID=did,
                    MARKER=DomainReqHandler.MARKER_CLAIM_DEF,
                    SIGNATURE_TYPE=signatureType,
                    SCHEMA_SEQ_NO=schemaSeqNo)\
            .encode()

    def _encodeValue(self, value, seqNo, txnTime):
        return self.stateSerializer.serialize({
            DomainReqHandler.LAST_SEQ_NO: seqNo,
            DomainReqHandler.LAST_UPDATE_TIME: txnTime,
            DomainReqHandler.VALUE: value
        })

    @staticmethod
    def transform_txn_for_ledger(txn):
        """
        Some transactions need to be transformed before they can be stored in the
        ledger, eg. storing certain payload in another data store and only its
        hash in the ledger
        """
        if txn[TXN_TYPE] == ATTRIB:
            txn = DomainReqHandler.hash_attrib_txn(txn)
        return txn

    @staticmethod
    def hash_attrib_txn(txn):
        # Creating copy of result so that `RAW`, `ENC` or `HASH` can be
        # replaced by their hashes. We do not insert actual attribute data
        # in the ledger but only the hash of it.
        txn = deepcopy(txn)

        attr_key, value = DomainReqHandler._parse_attr(txn)
        hashedVal = DomainReqHandler._hashOf(value) if value else ''

        if RAW in txn:
            txn[RAW] = hashedVal
        elif ENC in txn:
            txn[ENC] = hashedVal
        elif HASH in txn:
            txn[HASH] = txn[HASH]
        return txn

    @staticmethod
    def make_result(request, data, last_seq_no, update_time, proof):
        result = {**request.operation, **{
            DATA: data,
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
            f.SEQ_NO.nm: last_seq_no,
            TXN_TIME: update_time,
            STATE_PROOF: proof
        }}
        # Do not inline please, it makes debugging easier
        return result

    @staticmethod
    def _parse_attr(txn):
        raw = txn.get(RAW)
        if raw:
            data = attrib_raw_data_serializer.deserialize(raw)
            # To exclude user-side formatting issues
            re_raw = attrib_raw_data_serializer.serialize(data,
                                                          toBytes=False)
            key, _ = data.popitem()
            return key, re_raw
        enc = txn.get(ENC)
        if enc:
            return DomainReqHandler._hashOf(enc), enc
        hsh = txn.get(HASH)
        if hsh:
            return hsh, None
        raise ValueError("One of 'raw', 'enc', 'hash' "
                         "fields of ATTR must present")
