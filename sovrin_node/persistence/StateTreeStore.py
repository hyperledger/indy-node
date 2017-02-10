from plenum.common.state import State
from sovrin_common.txn import TXN_TYPE, \
    TARGET_NYM, allOpKeys, validTxnTypes, ATTRIB, SPONSOR, NYM,\
    ROLE, STEWARD, GET_ATTR, DISCLO, DATA, GET_NYM, \
    TXN_ID, TXN_TIME, reqOpKeys, GET_TXNS, LAST_TXN, TXNS, \
    getTxnOrderedFields, SCHEMA, GET_SCHEMA, openTxns, \
    ISSUER_KEY, GET_ISSUER_KEY, REF, TRUSTEE, TGB, IDENTITY_TXN_TYPES, \
    CONFIG_TXN_TYPES, POOL_UPGRADE, ACTION, START, CANCEL, SCHEDULE, \
    NODE_UPGRADE, COMPLETE, FAIL, HASH, ENC, RAW, NONCE
import json
from hashlib import sha256

# TODO: think about encapsulating State in it,
# instead of direct accessing to it in node

class StateTreeStore:
    """
    Class for putting transactions into state tree
    Akin to IdentityGraph
    """

    def __init__(self, state: State):
        assert state is not None
        self.state = state

    def addTxn(self, txn) -> None:
        """
        Add transaction to state store
        """

        {
            NYM:        self._addNym,
            ATTRIB:     self._addAttrib,
            SCHEMA:     self._addSchema,
            ISSUER_KEY: self._addIssuerKey
        }[txn[TXN_TYPE]](txn)


    def _addNym(self, txn):
        assert txn[TXN_TYPE] == NYM
        raise NotImplementedError

    def _addAttrib(self, txn):
        assert txn[TXN_TYPE] == ATTRIB

        def parse(txn):
            raw = txn.get(RAW)
            if raw:
                data = json.loads(raw)
                key, value = data.items()[0]  # only one attr per txn, yes
                return key, value
            enc = txn.get(ENC)
            if enc:
                return (enc, enc)
            hash = txn.get(HASH)
            if hash:
                return hash, None
            raise ValueError("One of 'raw', 'enc', 'hash' "
                             "fields of ATTR must present")

        rawKey, value = parse(txn)
        key = sha256(rawKey.encode()).hexdigest()
        self.state.set(key, value)

    def _addSchema(self, txn):
        assert txn[TXN_TYPE] == SCHEMA
        raise NotImplementedError

    def _addIssuerKey(self, txn):
        assert txn[TXN_TYPE] == ISSUER_KEY
        raise NotImplementedError
