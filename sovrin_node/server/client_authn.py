from copy import deepcopy
from hashlib import sha256

from plenum.common.exceptions import UnknownIdentifier
from plenum.common.txn import TXN_TYPE, RAW, ENC, HASH, VERKEY
from plenum.server.client_authn import NaclAuthNr
from sovrin_common.txn import ATTRIB
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.persistence.state_tree_store import StateTreeStore


class TxnBasedAuthNr(NaclAuthNr):
    """
    Transaction-based client authenticator.
    """
    def __init__(self, cache: IdrCache, stateStore: StateTreeStore):
        self.cache = cache
        self.stateStore = stateStore

    def serializeForSig(self, msg, topLevelKeysToIgnore=None):
        if msg["operation"].get(TXN_TYPE) == ATTRIB:
            msgCopy = deepcopy(msg)
            keyName = {RAW, ENC, HASH}.intersection(
                set(msgCopy["operation"].keys())).pop()
            msgCopy["operation"][keyName] = sha256(msgCopy["operation"][keyName]
                                                   .encode()).hexdigest()
            return super().serializeForSig(msgCopy,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)
        else:
            return super().serializeForSig(msg,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)

    def addIdr(self, identifier, verkey, role=None):
        raise RuntimeError('Add verification keys through the NYM txn')

    def getVerkey(self, identifier):
        try:
            verkey = self.cache.getVerkey(identifier)
        except KeyError:

        return verkey
        # nym = self.storage.getNym(identifier)
        # if not nym:
        #     raise UnknownIdentifier(identifier)
        # verkey = nym.oRecordData.get(VERKEY) or ''
        # return verkey
