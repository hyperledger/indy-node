from plenum.common.exceptions import NotConnectedToAny
from indy_common.identity import Identity


class Caching:
    """
    Mixin for agents to manage caching.

    Dev notes: Feels strange to inherit from WalletedAgent, but self-typing
    doesn't appear to be implemented in Python yet.
    """

    def getClient(self):
        if self.client:
            return self.client
        else:
            raise NotConnectedToAny

    def getIdentity(self, identifier):
        identity = Identity(identifier=identifier)
        req = self.wallet.requestIdentity(identity,
                                          sender=self.wallet.defaultId)
        self.getClient().submitReqs(req)
        return req
