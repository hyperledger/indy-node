from abc import abstractmethod

from plenum.persistence.client_req_rep_store import ClientReqRepStore as \
    PClientReqRepStore


class ClientReqRepStore(PClientReqRepStore):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def setLastTxnForIdentifier(self, identifier, value: str):
        pass

    @abstractmethod
    def getLastTxnForIdentifier(self, identifier):
        pass
