from copy import deepcopy
from hashlib import sha256

from plenum.common.exceptions import UnknownIdentifier
from plenum.common.types import OPERATION
from plenum.common.constants import TXN_TYPE, RAW, ENC, HASH, VERKEY
from plenum.server.client_authn import NaclAuthNr

from indy_common.constants import ATTRIB
from indy_node.persistence.idr_cache import IdrCache
# from indy_node.persistence.state_tree_store import StateTreeStore


class TxnBasedAuthNr(NaclAuthNr):
    """
    Transaction-based client authenticator.
    """

    def __init__(self, cache: IdrCache):
        self.cache = cache

    def serializeForSig(self, msg, topLevelKeysToIgnore=None):
        if msg[OPERATION].get(TXN_TYPE) == ATTRIB:
            msgCopy = deepcopy(msg)
            keyName = {RAW, ENC, HASH}.intersection(
                set(msgCopy[OPERATION].keys())).pop()
            msgCopy[OPERATION][keyName] = sha256(
                msgCopy[OPERATION][keyName].encode()).hexdigest()
            return super().serializeForSig(msgCopy,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)
        else:
            return super().serializeForSig(msg,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)

    def addIdr(self, identifier, verkey, role=None):
        raise RuntimeError('Add verification keys through the NYM txn')

    def getVerkey(self, identifier):
        try:
            verkey = self.cache.getVerkey(identifier, isCommitted=False)
        except KeyError:
            return None
        return verkey
