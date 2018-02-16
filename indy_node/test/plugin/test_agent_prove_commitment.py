from indy_client.test.conftest import nodeSet
from indy_node.test.plugin.test_policy_creation import policy_created


# TODO: Need an efficient way to update the accumulator
def test_agent_update_its_PROVE_commitment(looper, nodeSet, agent1_wallet,
                                           agent1_client, policy_created):
    """
    An agent should be able to update it's commitment in the accumulator.
    Test with an agent with **only** PROVE authorisation. Also check that
    agent cannot update any other agent's commitment
    """


def test_only_agent_can_update_its_PROVE_commitment():
    """
    No agent with any authorisations, ADMIN or otherwise can update the
    commitment of any other agent in the accumulator.
    Test with an agent with ADMIN, PROVE_GRANT, PROVE_REVOKE authorisation.
    """
