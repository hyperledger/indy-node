
from indy_common.identity import Identity
from stp_core.types import Identifier


class TrustAnchoring:
    """
    Mixin to add trust anchoring behaviors to a Wallet
    """

    def __init__(self):
        self._trustAnchored = {}  # type: Dict[Identifier, Identity]

    def createIdInWallet(self, idy: Identity):
        if idy.identifier in self._trustAnchored:
            del self._trustAnchored[idy.identifier]
        self._trustAnchored[idy.identifier] = idy

    def addTrustAnchoredIdentity(self, idy: Identity):
        self.createIdInWallet(idy)
        self._sendIdReq(idy)

    def _sendIdReq(self, idy):
        req = idy.ledgerRequest()
        if req:
            if not req._identifier:
                req._identifier = self.defaultId
            self.pendRequest(req, idy.identifier)
        return len(self._pending)

    def updateTrustAnchoredIdentity(self, idy):
        storedId = self._trustAnchored.get(idy.identifier)
        if storedId:
            storedId.seqNo = None
        else:
            self.createIdInWallet(idy)
        self._sendIdReq(idy)

    def getTrustAnchoredIdentity(self, idr):
        return self._trustAnchored.get(idr)
