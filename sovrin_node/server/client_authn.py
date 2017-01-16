from hashlib import sha256
from copy import deepcopy

from plenum.common.exceptions import UnknownIdentifier
from plenum.common.txn import TXN_TYPE, RAW, ENC, HASH
from plenum.server.client_authn import NaclAuthNr

from sovrin_common.txn import ATTRIB
from sovrin_common.persistence.identity_graph import IdentityGraph


class TxnBasedAuthNr(NaclAuthNr):
    """
    Transaction-based client authenticator.
    """
    def __init__(self, storage: IdentityGraph):
        self.storage = storage

    def serializeForSig(self, msg):
        if msg["operation"].get(TXN_TYPE) == ATTRIB:
            msgCopy = deepcopy(msg)
            keyName = {RAW, ENC, HASH}.intersection(
                set(msgCopy["operation"].keys())).pop()
            msgCopy["operation"][keyName] = sha256(msgCopy["operation"][keyName]
                                                   .encode()).hexdigest()
            return super().serializeForSig(msgCopy)
        else:
            return super().serializeForSig(msg)

    def addClient(self, identifier, verkey, role=None):
        raise RuntimeError('Add verification keys through the ADDNYM txn')

    def getVerkey(self, identifier):
        nym = self.storage.getNym(identifier)
        if not nym:
            raise UnknownIdentifier(identifier)
        verkey = nym.oRecordData.get('verkey') or ''
        return verkey
