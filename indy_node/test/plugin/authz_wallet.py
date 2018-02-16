# This is a temporary class, used for testing, the real wallet would be in indy-sdk
from indy_node.test.plugin.helper import gen_random_policy_address, \
    gen_random_agent_secret, gen_random_commitment
from indy_client.client.wallet.wallet import Wallet
from plenum.common.signer_simple import SimpleSigner


class AuthzWallet(Wallet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_addresses = {}

    def add_new_policy_address(self):
        # TODO: In the actual wallet, generate a correct size policy address.
        a = gen_random_policy_address()
        self.policy_addresses[a] = {}
        return a

    def add_new_agent_key(self, policy_address):
        secret = gen_random_agent_secret()
        signer = SimpleSigner()
        # TODO: In the actual wallet, generate a prime double commitment over
        # the secret
        self.policy_addresses[policy_address] = (secret,
                                                 gen_random_commitment(),
                                                 signer)
        return signer.verkey
