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

from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepo
from anoncreds.protocol.repo.public_repo import PublicRepo
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory
from indy_client.anon_creds.indy_public_repo import IndyPublicRepo
from indy_client.client.wallet.wallet import Wallet


class IndyIssuer(Issuer):
    def __init__(self, client, wallet: Wallet, attrRepo: AttributeRepo,
                 publicRepo: PublicRepo = None):
        publicRepo = publicRepo or IndyPublicRepo(client=client,
                                                  wallet=wallet)
        issuerWallet = IndyIssuerWalletInMemory(wallet.name, publicRepo)

        super().__init__(issuerWallet, attrRepo)

    def prepareForWalletPersistence(self):
        # TODO: If we don't set self.wallet._repo.client to None,
        # it hangs during wallet persistence, based on findings, it seems,
        # somewhere it hangs during persisting client._ledger and
        # client.ledgerManager
        self.wallet._repo.client = None

    def restorePersistedWallet(self, issuerWallet):
        curRepoClient = self.wallet._repo.client
        self.wallet = issuerWallet
        self._primaryIssuer._wallet = issuerWallet
        self._nonRevocationIssuer._wallet = issuerWallet
        self.wallet._repo.client = curRepoClient


class IndyIssuerWalletInMemory(IssuerWalletInMemory):

    def __init__(self, name, pubRepo):

        IssuerWalletInMemory.__init__(self, name, pubRepo)

        # available claims to anyone whose connection is accepted by the agent
        self.availableClaimsToAll = []

        # available claims only for certain invitation (by nonce)
        self.availableClaimsByNonce = {}

        # available claims only for certain invitation (by nonce)
        self.availableClaimsByInternalId = {}

        # mapping between specific identifier and available claims which would
        # have been available once they have provided requested information
        # like proof etc.
        self.availableClaimsByIdentifier = {}

        self._proofRequestsSchema = {}  # Dict[str, Dict[str, any]]
