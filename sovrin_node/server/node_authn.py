import functools

from ledger.ledger import Ledger
from plenum.common.exceptions import UnknownIdentifier
from plenum.common.txn import TARGET_NYM, VERKEY
from plenum.server.client_authn import NaclAuthNr


class NodeAuthNr(NaclAuthNr):
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    @functools.lru_cache(maxsize=20)
    def getVerkey(self, identifier):
        # TODO: This is very inefficient
        verkey = None
        found = False
        for txn in self.ledger.getAllTxn().values():
            if txn[TARGET_NYM] == identifier:
                found = True
                if txn.get(VERKEY):
                    verkey = txn[VERKEY]

        if not found:
            raise UnknownIdentifier(identifier)
        verkey = verkey or identifier
        return verkey
