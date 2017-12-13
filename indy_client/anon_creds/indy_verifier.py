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
