import pytest

from indy_client.test.conftest import nodeSet
from indy_node.server.plugin.agent_authz.constants import ADDRESS, COMMITMENT, \
    AGENT_AUTHZ, AUTHORIZATION
from indy_node.test.plugin.helper import gen_random_commitment, \
    check_policy_txn_updates_state_and_cache
from indy_node.test.plugin.test_policy_creation import policy_created
from plenum.common.constants import TXN_TYPE, VERKEY
from plenum.common.signer_simple import SimpleSigner
from plenum.test.helper import send_signed_requests, sign_requests, \
    waitForSufficientRepliesForRequests


def give_grant_prove(looper, addr, sender_verkey, wallet, client):
    verkey, _ = wallet.addIdentifier(signer=SimpleSigner())
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        AUTHORIZATION: 4,  # PROVE_GRANT authorisation
    }
    requests = send_signed_requests(client, sign_requests(
        wallet, [op, ], identifier=sender_verkey))
    waitForSufficientRepliesForRequests(looper, client,
                                        requests=requests)
    return addr, verkey, 4


def give_revoke_prove(looper, addr, sender_verkey, wallet, client):
    verkey, _ = wallet.addIdentifier(signer=SimpleSigner())
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        AUTHORIZATION: 8,  # PROVE_REVOKE authorisation
    }
    requests = send_signed_requests(client, sign_requests(
        wallet, [op, ], identifier=sender_verkey))
    waitForSufficientRepliesForRequests(looper, client,
                                        requests=requests)
    return addr, verkey, 8


def give_prove(looper, addr, sender_verkey, wallet, client):
    verkey, _ = wallet.addIdentifier(signer=SimpleSigner())
    commitment = gen_random_commitment()
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        AUTHORIZATION: 2,  # PROVE authorisation
        COMMITMENT: commitment,
    }
    requests = send_signed_requests(client, sign_requests(
        wallet, [op, ], identifier=sender_verkey))
    waitForSufficientRepliesForRequests(looper, client,
                                        requests=requests)
    return addr, verkey, 2, commitment


def give_admin(looper, addr, sender_verkey, wallet, client):
    verkey, _ = wallet.addIdentifier(signer=SimpleSigner())
    commitment = gen_random_commitment()
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        AUTHORIZATION: 1,  # ADMIN authorisation
        COMMITMENT: commitment,
    }
    requests = send_signed_requests(client, sign_requests(
        wallet, [op, ], identifier=sender_verkey))
    waitForSufficientRepliesForRequests(looper, client, requests=requests)
    return addr, verkey, 1, commitment


def revoke_prove(looper, addr, sender_verkey, prover_verkey, wallet, client):
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: prover_verkey,
        AUTHORIZATION: 0,  # No authorisation
    }
    requests = send_signed_requests(client, sign_requests(
        wallet, [op, ], identifier=sender_verkey))
    waitForSufficientRepliesForRequests(looper, client,
                                        requests=requests)


@pytest.fixture(scope='module')
def prove_grant_given(looper, nodeSet, agent1_wallet, agent1_client,
                      policy_created):
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth = give_grant_prove(looper, addr, admin_verkey,
                                       agent1_wallet, agent1_client)
    assert auth == 4
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 4, 0)
    return addr, verkey, 4


@pytest.fixture(scope='module')
def prove_revoke_given(looper, nodeSet, agent1_wallet, agent1_client,
                       policy_created):
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth = give_revoke_prove(looper, addr, admin_verkey,
                                       agent1_wallet, agent1_client)
    assert auth == 8
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 8, 0)
    return addr, verkey, 8


def test_grant_PROVE_GRANT_auth(looper, nodeSet, policy_created,
                                prove_grant_given):
    """
    Only an admin should be able to grant an agent pubkey PROVE_GRANT authorisation
    Have each role except admin make attempts and fail.
    Test this with a new agent as well as with an agent with PROVE auth
    """
    addr, admin_verkey, admin_auth, admin_commitment = policy_created
    _, granter_verkey, granter_auth = prove_grant_given
    # TODO: Add fail attempts


def test_grant_PROVE_REVOKE_auth(looper, nodeSet, policy_created,
                                 prove_revoke_given):
    """
    Only an admin should be able to revoke an agent pubkey's PROVE_REVOKE authorisation
    Have each role except admin make attempts and fail
    Test this with a new agent as well as with an agent with PROVE auth
    """
    addr, admin_verkey, admin_auth, admin_commitment = policy_created
    _, revoker_verkey, revoker_auth = prove_revoke_given
    # TODO: Add fail attempts


def test_grant_PROVE_auth(looper, nodeSet, agent1_wallet,
                          agent1_client, policy_created, prove_grant_given):
    """
    Only an admin or an agent with PROVE_GRANT should be able to give an agent
    pubkey a PROVE authorisation.
    Have each role except the 2 mentioned above make attempts and fail
    """
    # Admin gives PROVE
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth, commitment = give_prove(looper, addr, admin_verkey,
                                             agent1_wallet, agent1_client)
    assert auth == 2
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 2,
                                             commitment)

    # Agent with PROVE_GRANT gives PROVE
    _, granter_verkey, granter_auth = prove_grant_given
    _, verkey, auth, commitment = give_prove(looper, addr, granter_verkey,
                                             agent1_wallet, agent1_client)
    assert auth == 2
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 2,
                                             commitment)
    # TODO: Add fail attempts


def test_revoke_PROVE_auth(looper, nodeSet, agent1_wallet, agent1_client,
                           policy_created, prove_revoke_given):
    """
    Only an admin or an agent with PROVE_REVOKE should be able to revoke an agent
    pubkey's PROVE authorisation
    Have each role except the 2 mentioned above make attempts and fail
    """
    # Admin gives PROVE
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth, commitment = give_prove(looper, addr, admin_verkey,
                                             agent1_wallet, agent1_client)
    # Admin revokes PROVE
    revoke_prove(looper, addr, admin_verkey, verkey, agent1_wallet,
                 agent1_client)
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 0, 0)

    # Admin gives PROVE
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth, commitment = give_prove(looper, addr, admin_verkey,
                                             agent1_wallet, agent1_client)
    # Revoker revokes PROVE
    _, revoker_verkey, _ = prove_revoke_given
    revoke_prove(looper, addr, revoker_verkey, verkey, agent1_wallet,
                 agent1_client)
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 0, 0)

    # TODO: Add fail attempts


def test_revoke_PROVE_GRANT_auth(looper, nodeSet, agent1_wallet,
                                 agent1_client, policy_created, prove_grant_given):
    """
    Only an admin should be able to revoke an agent pubkey's PROVE_GRANT authorisation
    Have each role except admin make attempts and fail.
    """
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth, commitment = give_prove(looper, addr, admin_verkey,
                                             agent1_wallet, agent1_client)
    # TODO


def test_revoke_PROVE_REVOKE_auth():
    """
    Only an admin should be able to revoke an agent pubkey's PROVE_REVOKE authorisation
    Have each role except admin make attempts and fail.
    """
    pass


def test_self_revoke_PROVE_auth():
    """
    An agent should be able to revoke it's own PROVE authorisation.
    Have an agent pubkey with **only** PROVE authorisation and then make it
    revoke it's PROVE authorisation
    """


def test_grant_ADMIN_auth(looper, nodeSet, agent1_wallet,
                          agent1_client, policy_created):
    """
    An admin can grant/revoke ADMIN authorisation to any number of agents;
    all admins are equal.
    Let an admin grant ADMIN to 2 more agents, then let one of those agents
    revoke ADMIN auth from both the old and one of the new admin. Revoke all
    auths of old admin but only keep PROVE auth of the new agent.
    """
    addr, admin_verkey, _, _ = policy_created
    _, verkey, auth, commitment = give_admin(looper, addr, admin_verkey,
                                  agent1_wallet, agent1_client)
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 1,
                                             commitment)
