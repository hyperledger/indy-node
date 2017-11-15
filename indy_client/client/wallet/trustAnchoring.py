#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#


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
            if not req.identifier:
                req.identifier = self.defaultId
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
