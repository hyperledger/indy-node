from anoncreds.protocol.repo.public_repo import PublicRepo

from anoncreds.protocol.verifier import Verifier
from anoncreds.protocol.wallet.wallet import WalletInMemory

from sovrin_client.anon_creds.sovrin_public_repo import SovrinPublicRepo
from sovrin_client.client.wallet.wallet import Wallet


class SovrinVerifier(Verifier):
    def __init__(self, client, wallet: Wallet, publicRepo: PublicRepo = None):
        publicRepo = publicRepo or SovrinPublicRepo(client=client, wallet=wallet)
        verifierWallet = WalletInMemory(wallet.defaultId, publicRepo)
        super().__init__(verifierWallet)
