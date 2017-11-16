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

from anoncreds.protocol.repo.public_repo import PublicRepo

from anoncreds.protocol.verifier import Verifier
from anoncreds.protocol.wallet.wallet import WalletInMemory

from indy_client.anon_creds.indy_public_repo import IndyPublicRepo
from indy_client.client.wallet.wallet import Wallet


class IndyVerifier(Verifier):
    def __init__(self, client, wallet: Wallet, publicRepo: PublicRepo = None):
        publicRepo = publicRepo or IndyPublicRepo(
            client=client, wallet=wallet)
        verifierWallet = WalletInMemory(wallet.defaultId, publicRepo)
        super().__init__(verifierWallet)
