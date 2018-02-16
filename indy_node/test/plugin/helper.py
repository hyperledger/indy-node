import random

from indy_node.server.plugin.agent_authz.domain_req_handler import \
    DomainReqHandlerWithAuthz
from plenum.common.constants import DOMAIN_LEDGER_ID

from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import randomString

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def gen_random_commitment():
    return random.choice(PRIMES)


def gen_random_policy_address():
    return random.randint(100, 1000000)


def gen_random_verkey():
    return SimpleSigner().verkey


def gen_random_agent_secret():
    return random.randint(30, 99)


def check_policy_txn_updates_state_and_cache(nodes, policy_address, verkey,
                                             auth, commitment):
    for node in nodes:
        state = node.getState(DOMAIN_LEDGER_ID)
        req_handler = node.get_req_handler(ledger_id=DOMAIN_LEDGER_ID)
        val = DomainReqHandlerWithAuthz._get_policy_from_state(state,
                                                               policy_address,
                                                               is_committed=True)
        for (v, a, c) in val:
            if verkey.encode() == v:
                assert (verkey.encode(), auth, commitment) == (v, a, c)
        assert req_handler.agent_authz_cache.get_agent_details(
            policy_address, verkey, True) == (auth, commitment)
