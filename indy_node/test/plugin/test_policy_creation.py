import pytest

from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, ADDRESS, \
    AUTHORIZATION, COMMITMENT
from indy_node.server.plugin.agent_authz.messages.types import \
    MAX_POLICY_ADDRESS, MAX_COMMITMENT
from indy_node.test.plugin.helper import gen_random_commitment, \
    gen_random_verkey, gen_random_policy_address, PRIMES, \
    check_policy_txn_updates_state_and_cache
from plenum.common.constants import TXN_TYPE, VERKEY
from plenum.common.signer_simple import SimpleSigner
from plenum.test.helper import send_signed_requests, \
    waitReqNackFromPoolWithReason, sign_requests, \
    waitForSufficientRepliesForRequests, waitRejectFromPoolWithReason


def send_op_and_wait_for_nack(looper, nodes, op, client, wallet, reason):
    send_signed_requests(client, sign_requests(wallet, [op, ]))
    waitReqNackFromPoolWithReason(looper, nodes, client, reason)


def send_op_and_wait_for_reject(looper, nodes, op, client, wallet, reason):
    send_signed_requests(client, sign_requests(wallet, [op, ]))
    waitRejectFromPoolWithReason(looper, nodes, client, reason)


def test_new_authz_policy_bad_address(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    The new policy txn has no policy address or invalid policy address, it fails
    """
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1,
        COMMITMENT: gen_random_commitment(),
    }
    send_op_and_wait_for_nack(looper, nodeSet, op, agent1_client,
                              agent1_wallet, 'missed fields - {}'.format(ADDRESS))

    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: str(MAX_POLICY_ADDRESS+10),
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1,
        COMMITMENT: gen_random_commitment(),
    }
    send_op_and_wait_for_nack(looper, nodeSet, op, agent1_client, agent1_wallet,
                              'should not be greater than {}'.format(MAX_POLICY_ADDRESS))


def test_new_authz_policy_bad_commitment(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    The new policy txn has no commitment or invalid (composite or large size)
    commitment, it fails
    """

    # No commitment in policy creation txn
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1
    }
    send_op_and_wait_for_reject(looper, nodeSet, op, agent1_client,
                                agent1_wallet, 'missed fields - {}'.format(COMMITMENT))

    # Composite commitment in policy creation txn
    composite_commitment = 4
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1,
        COMMITMENT: composite_commitment,
    }
    send_op_and_wait_for_nack(looper, nodeSet, op, agent1_client, agent1_wallet,
                              'should be prime, found {} instead'.
                              format(composite_commitment))

    # Too large commitment in policy creation txn
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1,
        COMMITMENT: str(MAX_COMMITMENT+1),
    }
    send_op_and_wait_for_nack(looper, nodeSet, op, agent1_client, agent1_wallet,
                              'should not be greater than {}'.format(MAX_COMMITMENT))


def test_new_authz_policy_has_bad_verkey(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    The new policy txn has a verkey different from `identifier`, it fails
    """
    # Composite commitment in policy creation txn
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        VERKEY: gen_random_verkey(),
        AUTHORIZATION: 1,
        COMMITMENT: 29,
    }
    send_op_and_wait_for_reject(looper, nodeSet, op, agent1_client,
                                agent1_wallet,
                                'either omit {} or make it same as {}'.
                                format(VERKEY, agent1_wallet.defaultId))


def test_new_authz_policy_has_invalid_authz_bits(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    The new policy txn has a invalid authorisation bits, less bits set to 1
    """
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        AUTHORIZATION: 2,
        COMMITMENT: 29,
    }
    send_op_and_wait_for_reject(looper, nodeSet, op, agent1_client,
                                agent1_wallet, "should have the 0'th bit set")

    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: gen_random_policy_address(),
        AUTHORIZATION: 4,
        COMMITMENT: 29,
    }
    send_op_and_wait_for_reject(looper, nodeSet, op, agent1_client,
                                agent1_wallet, "should have the 0'th bit set")


@pytest.fixture(scope='module')
def policy_created(looper, nodeSet, agent1_wallet, agent1_client):
    addr = gen_random_policy_address()
    verkey, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    commitment = gen_random_commitment()
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        COMMITMENT: commitment,
    }
    requests = send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op, ], identifier=verkey))
    waitForSufficientRepliesForRequests(looper, agent1_client,
                                        requests=requests)
    return addr, verkey, 1, commitment


def test_new_authz_policy_without_default_values(looper,
                                      nodeSet, policy_created):
    """
    A correct agent authz transaction updates the ledger, state and cache
    appropriately. Does not send value for verkey or authorisation
    :return:
    """
    # Generate a new policy address and verkey
    addr, verkey, auth, commitment = policy_created
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, auth,
                                             commitment)


def test_new_authz_policy_with_correct_verkey(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    A correct agent authz transaction updates the ledger, state and cache
    appropriately. Does not send value for authorisation but verkey is same as identifier.
    :return:
    """
    addr = gen_random_policy_address()
    verkey, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    # BigNumber, so a string
    commitment = "318028647963126151329853788044970037553383723548483991111562082327990638642710893355904748171562443528303700560839933521244978396415095418730498962422748911233060199731345351794902617682381377504128982684873285344278700181318498672093457626984884328901609908211755665042560103660590284040739154480985634957587"
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        COMMITMENT: commitment,
    }
    requests = send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op, ], identifier=verkey))
    waitForSufficientRepliesForRequests(looper, agent1_client,
                                        requests=requests)
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 1,
                                             int(commitment))


def test_new_authz_policy_with_correct_authz_bits(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    A correct agent authz transaction updates the ledger, state and cache
    appropriately. Does not send value for verkey but authorisation has admin
    permissions.
    :return:
    """
    requests = []
    addr1 = gen_random_policy_address()
    auth1 = 1
    commitment1 = gen_random_commitment()
    verkey1, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    op1 = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr1,
        AUTHORIZATION: auth1,
        COMMITMENT: commitment1,
    }
    requests.extend(send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op1, ], identifier=verkey1)))

    addr2 = gen_random_policy_address()
    auth2 = 3
    commitment2 = gen_random_commitment()
    verkey2, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    op2 = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr2,
        AUTHORIZATION: auth2,
        COMMITMENT: commitment2,
    }
    requests.extend(send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op2, ], identifier=verkey2)))

    addr3 = gen_random_policy_address()
    auth3 = 101
    commitment3 = gen_random_commitment()
    verkey3, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    op3 = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr3,
        AUTHORIZATION: auth3,
        COMMITMENT: commitment3,
    }
    requests.extend(send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op3, ], identifier=verkey3)))

    waitForSufficientRepliesForRequests(looper, agent1_client,
                                        requests=requests)
    check_policy_txn_updates_state_and_cache(nodeSet, addr1, verkey1, auth1,
                                             commitment1)
    check_policy_txn_updates_state_and_cache(nodeSet, addr2, verkey2, auth2,
                                             commitment2)
    check_policy_txn_updates_state_and_cache(nodeSet, addr3, verkey3, auth3,
                                             commitment3)


def test_new_authz_policy_with_correct_verkey_and_authz_bits(looper,
                                      nodeSet,
                                      agent1_wallet,
                                      agent1_client):
    """
    A correct agent authz transaction updates the ledger, state and cache
    appropriately. Send correct values for both authorisation and verkey
    :return:
    """
    addr = gen_random_policy_address()
    verkey, _ = agent1_wallet.addIdentifier(signer=SimpleSigner())
    commitment = gen_random_commitment()
    op = {
        TXN_TYPE: AGENT_AUTHZ,
        ADDRESS: addr,
        VERKEY: verkey,
        AUTHORIZATION: 1,
        COMMITMENT: commitment,
    }
    requests = send_signed_requests(agent1_client, sign_requests(
        agent1_wallet, [op, ], identifier=verkey))
    waitForSufficientRepliesForRequests(looper, agent1_client,
                                        requests=requests)
    check_policy_txn_updates_state_and_cache(nodeSet, addr, verkey, 1,
                                             commitment)
