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
