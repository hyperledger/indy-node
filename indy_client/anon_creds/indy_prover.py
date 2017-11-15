from anoncreds.protocol.prover import Prover
from anoncreds.protocol.repo.public_repo import PublicRepo
from anoncreds.protocol.wallet.prover_wallet import ProverWalletInMemory
from indy_client.anon_creds.indy_public_repo import IndyPublicRepo
from indy_client.client.wallet.wallet import Wallet


class IndyProver(Prover):
    def __init__(self, client, wallet: Wallet, publicRepo: PublicRepo = None):
        publicRepo = publicRepo or IndyPublicRepo(
            client=client, wallet=wallet)
        proverWallet = ProverWalletInMemory(wallet.name, publicRepo)
        super().__init__(proverWallet)
