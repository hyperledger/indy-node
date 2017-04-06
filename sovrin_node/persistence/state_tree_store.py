import json

from stp_core.common.log import getlogger
from plenum.common.state import State
from plenum.common.constants import TXN_TYPE, DATA, HASH, ENC, RAW, TARGET_NYM
from sovrin_common.constants import ATTRIB, SCHEMA, ISSUER_KEY, REF
from plenum.common.types import f

# TODO: think about encapsulating State in it,
# instead of direct accessing to it in node

logger = getlogger()


class StateTreeStore:
    """
    Class for adding or getting transactions from state tree
    Akin to IdentityGraph
    """

    MARKER_ATTR = "\01"
    MARKER_SCHEMA = "\02"
    MARKER_IPK = "\03"
    LAST_SEQ_NO = "last_seq_no"
    VALUE = "value"

    REQUIRED_TXN_FIELDS = {
        TXN_TYPE,
        TARGET_NYM,
        f.SEQ_NO.nm
    }

    def __init__(self, state: State):
        assert state is not None
        self.state = state

    def lookup(self, path, isCommitted=True) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :return: data
        """
        assert path is not None
        raw = self.state.get(path, isCommitted).decode()
        value = raw[StateTreeStore.VALUE]
        lastSeqNo = raw[StateTreeStore.LAST_SEQ_NO]
        return value, lastSeqNo

    def addTxn(self, txn) -> None:
        """
        Add transaction to state store
        """
        assert self.REQUIRED_TXN_FIELDS.issubset(txn)
        {
            ATTRIB: self._addAttr,
            SCHEMA: self._addSchema,
            ISSUER_KEY: self._addIssuerKey,
        }.get(txn[TXN_TYPE], lambda *_: None)(txn)

    def _addAttr(self, txn) -> None:
        assert txn[TXN_TYPE] == ATTRIB
        did = txn.get(TARGET_NYM)

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
        path = self._makeAttrPath(did, attrName)
        seqNo = txn[f.SEQ_NO.nm]
        valueBytes = self._encodeValue(value, seqNo)
        self.state.set(path, valueBytes)

    def _addSchema(self, txn) -> None:
        assert txn[TXN_TYPE] == SCHEMA
        did = txn.get(TARGET_NYM)

        rawData = txn.get(DATA)
        if rawData is None:
            raise ValueError("Field 'data' is absent")
        jsonData = json.loads(rawData)
        schemaName = jsonData["name"]
        schemaVersion = jsonData["version"]
        path = self._makeSchemaPath(did, schemaName, schemaVersion)

        seqNo = txn[f.SEQ_NO.nm]
        valueBytes = self._encodeValue(rawData, seqNo)
        self.state.set(path, valueBytes)

    def _addIssuerKey(self, txn) -> None:
        assert txn[TXN_TYPE] == ISSUER_KEY
        did = txn.get(TARGET_NYM)

        schemaSeqNo = txn[REF]
        if schemaSeqNo is None:
            raise ValueError("'ref' field is absent, "
                             "but it must contain schema seq no")
        issuerKey = txn[DATA]
        if issuerKey is None:
            raise ValueError("'data' field is absent, "
                             "but it must contain key components")
        path = self._makeIssuerKeyPath(did, schemaSeqNo)

        seqNo = txn[f.SEQ_NO.nm]
        valueBytes = self._encodeValue(issuerKey, seqNo)
        self.state.set(path, valueBytes)

    def getAttr(self,
                did: str,
                key: str,
                isCommitted=True) -> (str, int):
        assert did is not None
        assert key is not None
        path = self._makeAttrPath(did, key)
        return self.lookup(path, isCommitted)

    def getSchema(self,
                  did: str,
                  schemaName: str,
                  schemaVersion: str,
                  isCommitted=True) -> (str, int):
        assert did is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = self._makeSchemaPath(did, schemaName, schemaVersion)
        return self.lookup(path, isCommitted)

    def getIssuerKey(self,
                     did: str,
                     schemaSeqNo: str,
                     isCommitted=True) -> (str, int):
        assert did is not None
        assert schemaSeqNo is not None
        path = self._makeIssuerKeyPath(did, schemaSeqNo)
        return self.lookup(path, isCommitted)

    @classmethod
    def _hashOf(cls, text) -> str:
        from hashlib import sha256
        return sha256(text.encode()).hexdigest()

    @classmethod
    def _makeAttrPath(cls, did, attrName) -> bytes:
        nameHash = cls._hashOf(attrName)
        return "{DID}:{MARKER}:{ATTR_NAME}" \
            .format(DID=did,
                    MARKER=StateTreeStore.MARKER_ATTR,
                    ATTR_NAME=nameHash) \
            .encode()

    @classmethod
    def _makeSchemaPath(cls, did, schemaName, schemaVersion) -> bytes:
        return "{DID}:{MARKER}:{SCHEMA_NAME}{SCHEMA_VERSION}" \
            .format(DID=did,
                    MARKER=StateTreeStore.MARKER_SCHEMA,
                    SCHEMA_NAME=schemaName,
                    SCHEMA_VERSION=schemaVersion) \
            .encode()

    @classmethod
    def _makeIssuerKeyPath(cls, did, schemaSeqNo) -> bytes:
        return "{DID}:{MARKER}:{SCHEMA_SEQ_NO}" \
                   .format(DID=did,
                           MARKER=StateTreeStore.MARKER_IPK,
                           SCHEMA_SEQ_NO=schemaSeqNo)\
                   .encode()

    @classmethod
    def _encodeValue(cls, value, seqNo):
        return json.dumps({
            StateTreeStore.LAST_SEQ_NO: seqNo,
            StateTreeStore.VALUE: value
        }).encode()