import pytest

from indy_node.test.plugin.helper import gen_random_commitment, \
    gen_random_policy_address, gen_random_verkey
from storage.test.conftest import parametrised_storage

from indy_node.server.plugin.agent_authz.cache import AgentAuthzCommitmentCache


@pytest.fixture()
def authz_cache(parametrised_storage) -> AgentAuthzCommitmentCache:
    cache = AgentAuthzCommitmentCache(parametrised_storage)
    return cache


def test_add_new_authorisation_with_and_without_commitment(authz_cache):
    """
    Also checks that bit for `PROVE` is not set if commitment not provided
    Checks that bit for `PROVE` is set if commitment provided
    """
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()

    # first bit is not set, so no PROVE authorisation, hence commitment
    # should not be passed
    auth_val = 4
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Passing commitment, raises an error
    with pytest.raises(ValueError):
        authz_cache.update_agent_details(gen_random_policy_address(),
                                         gen_random_verkey(), auth_val,
                                         gen_random_commitment())

    # first bit is set, so commitment should be passed
    auth_val = 2
    commitment = gen_random_commitment()
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val, commitment)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val,
                                                               commitment)

    # Not passing commitment, raises an error
    with pytest.raises(ValueError):
        authz_cache.update_agent_details(gen_random_policy_address(),
                                         gen_random_verkey(), auth_val)


def test_update_authorisation(authz_cache):
    """
    Checks that authorisation bitset can be updated and the bit for `PROVE` is
    compatible with value of commitment. Check for both cases, existing
    commitment and none
    """
    # Have a key with PROVE authorisation and commitment
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 10
    commitment = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val, commitment)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Update authorisation but still has PROVE set
    auth_val = 2
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Update authorisation but PROVE unset, the commitment should be removed
    auth_val = 4
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val,
                                                               0)

    # Have a key without PROVE authorisation (and no commitment)
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 4
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Update authorisation but still has PROVE unset
    auth_val = 8
    # No commitment
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Passing commitment raises error
    with pytest.raises(ValueError):
        authz_cache.update_agent_details(pol_addr, verkey, auth_val,
                                         gen_random_commitment())

    # Update authorisation but with PROVE set
    auth_val = 2
    # Not passing commitment raises error
    with pytest.raises(ValueError):
        authz_cache.update_agent_details(pol_addr, verkey, auth_val)

    # Pass commitment
    commitment = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val, commitment)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val,
                                                               commitment)


def test_add_commitment_to_existing_key(authz_cache):
    """
    A cache key has an authorisation bitset, check for both cases, existing
    commitment and none
    """
    # Have a key with PROVE authorisation and commitment
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 10
    commitment = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val, commitment)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Set a new commitment
    commitment_new = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, commitment=commitment_new)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val,
                                                               commitment_new)

    # Have a key without PROVE authorisation (and no commitment)
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 4
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Adding commitment raises an error
    commitment = gen_random_commitment()
    with pytest.raises(ValueError):
        authz_cache.update_agent_details(pol_addr, verkey,
                                         commitment=commitment)


def test_update_auth_and_commitment(authz_cache):
    # Have a key with PROVE authorisation and commitment
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 10
    commitment = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val, commitment)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val,
                                                               commitment)

    # Set a auth policy and new commitment
    auth_val_new = 2
    commitment_new = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val_new,
                                     commitment=commitment_new)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val_new,
                                                               commitment_new)

    # Have a key without PROVE authorisation (and no commitment)
    pol_addr = gen_random_policy_address()
    verkey = gen_random_verkey()
    auth_val = 4
    authz_cache.update_agent_details(pol_addr, verkey, auth_val)
    assert authz_cache.get_agent_details(pol_addr, verkey)[0] == auth_val

    # Set a auth policy and new commitment
    auth_val_new = 14
    commitment_new = gen_random_commitment()
    authz_cache.update_agent_details(pol_addr, verkey, auth_val_new,
                                     commitment=commitment_new)
    assert authz_cache.get_agent_details(pol_addr, verkey) == (auth_val_new,
                                                               commitment_new)


def test_set_get_accumulator(authz_cache):
    """
    Set the accumulator and get the value and compare that they are equal
    """
    value1 = 100
    authz_cache.set_accumulator(AgentAuthzCommitmentCache.ACCUMULATOR1_ID,
                                value1, is_committed=False)
    assert authz_cache.get_accumulator(AgentAuthzCommitmentCache.ACCUMULATOR1_ID,
                                       is_committed=False) == value1

    value2 = 200
    authz_cache.set_accumulator(AgentAuthzCommitmentCache.ACCUMULATOR2_ID,
                                value2, is_committed=False)
    assert authz_cache.get_accumulator(
        AgentAuthzCommitmentCache.ACCUMULATOR2_ID,
        is_committed=False) == value2

    with pytest.raises(KeyError):
        authz_cache.set_accumulator('invalid_id', 2201, is_committed=False)