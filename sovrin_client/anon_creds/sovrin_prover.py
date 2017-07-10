from anoncreds.protocol.prover import Prover
from anoncreds.protocol.repo.public_repo import PublicRepo
from anoncreds.protocol.wallet.prover_wallet import ProverWalletInMemory
from sovrin_client.anon_creds.sovrin_public_repo import SovrinPublicRepo
from sovrin_client.client.wallet.wallet import Wallet


class SovrinProver(Prover):
    def __init__(self, client, wallet: Wallet, publicRepo: PublicRepo = None):
        publicRepo = publicRepo or SovrinPublicRepo(client=client, wallet=wallet)
        proverWallet = ProverWalletInMemory(wallet.name, publicRepo)
        super().__init__(proverWallet)
