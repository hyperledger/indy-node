
from plenum.common.ledger import Ledger
from plenum.common.exceptions import UnknownIdentifier
from plenum.common.constants import TARGET_NYM, VERKEY
from plenum.common.txn_util import get_payload_data
from plenum.server.client_authn import NaclAuthNr


class NodeAuthNr(NaclAuthNr):
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def getVerkey(self, identifier):
        # TODO: This is very inefficient
        verkey = None
        found = False
        for _, txn in self.ledger.getAllTxn():
            txn_data = get_payload_data(txn)
            if txn_data[TARGET_NYM] == identifier:
                found = True
                if txn_data.get(VERKEY):
                    verkey = txn_data[VERKEY]

        if not found:
            raise UnknownIdentifier(identifier)
        verkey = verkey or identifier
        return verkey
