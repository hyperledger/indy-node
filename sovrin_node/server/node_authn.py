
from plenum.common.ledger import Ledger
from plenum.common.exceptions import UnknownIdentifier
from plenum.common.constants import TARGET_NYM, VERKEY
from plenum.server.client_authn import NaclAuthNr


class NodeAuthNr(NaclAuthNr):
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def getVerkey(self, identifier):
        # TODO: This is very inefficient
        verkey = None
        found = False
        for _, txn in self.ledger.getAllTxn():
            if txn[TARGET_NYM] == identifier:
                found = True
                if txn.get(VERKEY):
                    verkey = txn[VERKEY]

        if not found:
            raise UnknownIdentifier(identifier)
        verkey = verkey or identifier
        return verkey
