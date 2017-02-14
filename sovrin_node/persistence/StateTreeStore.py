from plenum.common.state import State
from plenum.common.log import getlogger
from sovrin_common.txn import TXN_TYPE, \
    TARGET_NYM, allOpKeys, validTxnTypes, ATTRIB, SPONSOR, NYM,\
    ROLE, STEWARD, GET_ATTR, DISCLO, DATA, GET_NYM, \
    TXN_ID, TXN_TIME, reqOpKeys, GET_TXNS, LAST_TXN, TXNS, \
    getTxnOrderedFields, SCHEMA, GET_SCHEMA, openTxns, \
    ISSUER_KEY, GET_ISSUER_KEY, REF, TRUSTEE, TGB, IDENTITY_TXN_TYPES, \
    CONFIG_TXN_TYPES, POOL_UPGRADE, ACTION, START, CANCEL, SCHEDULE, \
    NODE_UPGRADE, COMPLETE, FAIL, HASH, ENC, RAW, NONCE, DDO
import json

# TODO: think about encapsulating State in it,
# instead of direct accessing to it in node

logger = getlogger()

class StateTreeStore:
    """
    Class for putting transactions into state tree
    Akin to IdentityGraph
    """

    def __init__(self, state: State):
        assert state is not None
        self.state = state

    def addTxn(self, txn, did) -> None:
        """
        Add transaction to state store
        """

        {
            NYM:        self._addNym,
            ATTRIB:     self._addAttr,
            SCHEMA:     self._addSchema,
            ISSUER_KEY: self._addIssuerKey
        }[txn[TXN_TYPE]](txn, did)

    def _addNym(self, txn, did) -> None:
        """
        Processes nym transaction
        This implementation only stores ddo
        """
        assert txn[TXN_TYPE] == NYM

        ddo = txn.get(DDO)
        if ddo is not None:
            path = self._makeDdoPath(did)
            self.state.set(path, ddo)

    def _addAttr(self, txn, did) -> None:
        assert txn[TXN_TYPE] == ATTRIB
        assert did is not None

        def parse(txn):
            raw = txn.get(RAW)
            if raw:
                data = json.loads(raw)
                key, value = data.popitem()  # only one attr per txn, yes
                return key, value
            encOrHash = txn.get(ENC) or txn.get(HASH)
            if encOrHash:
                return encOrHash, encOrHash
            raise ValueError("One of 'raw', 'enc', 'hash' "
                             "fields of ATTR must present")

        attrName, value = parse(txn)
        path = self._makeAttrPath(did, attrName)
        self.state.set(path, value)

    def _addSchema(self, txn, did) -> None:
        assert txn[TXN_TYPE] == SCHEMA
        rawData = txn.get(DATA)
        if rawData is None:
            raise ValueError("Field 'data' is absent")
        jsonData = json.loads(rawData)

        # TODO: move them to constants?
        schemaName = jsonData["name"]
        schemaVersion = jsonData["version"]
        path = self._makeSchemaPath(did, schemaName, schemaVersion)
        self.state.set(path, rawData.encode())

    def _addIssuerKey(self, txn, did) -> None:
        assert txn[TXN_TYPE] == ISSUER_KEY

        schemaSeqNo = txn[REF]
        if schemaSeqNo is None:
            raise ValueError("'ref' field is absent, "
                             "but it must contain schema seq no")

        key = txn[DATA]
        if key is None:
            raise ValueError("'data' field is absent, "
                             "but it must contain key components")

        path = self._makeIssuerKeyPath(did, schemaSeqNo)
        self.state.set(path, key)

    def getSchema(self, did, schemaName: str, schemaVersion: str):
        assert did is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = self._makeSchemaPath(did, schemaName, schemaVersion)
        schema = self.state.get(path, isCommitted=False)
        return schema

    def getIssuerKey(self, did, schemaSeqNo):
        assert did is not None
        assert schemaSeqNo is not None
        path = self._makeIssuerKeyPath(did, schemaSeqNo)
        return self.state.get(path, isCommitted=False)

    def getAttr(self, key: str, did):
        assert did is not None
        assert key is not None
        path = self._makeAttrPath(did, key)
        return self.state.get(path, isCommitted=False)

    def getDdo(self, did) -> None:
        assert did is not None
        path = self._makeDdoPath(did)
        return self.state.get(path, isCommitted=False)

    @classmethod
    def _hashOf(cls, text) -> str:
        from hashlib import sha256
        return sha256(text.encode()).hexdigest()

    @classmethod
    def _makeAttrPath(cls, did, attrName) -> bytes:
        nameHash = cls._hashOf(attrName)
        return "{DID}:ATTR:{ATTR_NAME}" \
            .format(DID=did, ATTR_NAME=nameHash) \
            .encode()

    @classmethod
    def _makeDdoPath(cls, did) -> bytes:
        return "{DID}:DDO" \
            .format(DID=did) \
            .encode()

    @classmethod
    def _makeSchemaPath(cls, did, schemaName, schemaVersion) -> bytes:
        return "{DID}:SCHEMA:{SCHEMA_NAME}{SCHEMA_VERSION}" \
            .format(DID=did,
                    SCHEMA_NAME=schemaName,
                    SCHEMA_VERSION=schemaVersion) \
            .encode()

    @classmethod
    def _makeIssuerKeyPath(cls, did, schemaSeqNo) -> bytes:
        return "{DID}:IPK:{SCHEMA_SEQ_NO}" \
                   .format(DID=did, SCHEMA_SEQ_NO=schemaSeqNo)\
                   .encode()

    @classmethod
    def _makeRevocKeyPath(cls, did, schemaSeqNo, revRegSeqNo, time) -> bytes:
        return "{DID}:IPK:{SCHEMA_SEQ_NO}:REV_REG:{REV_REG_SEQ_NO}:{TIME}" \
            .format(DID=did,
                    SCHEMA_SEQ_NO=schemaSeqNo,
                    REV_REG_SEQ_NO=revRegSeqNo,
                    TIME=time) \
            .encode()
