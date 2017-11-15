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
