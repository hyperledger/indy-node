import logging

import pytest

from indy_client.test.agent.conftest import check_accept_request

concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]

whitelist = ["is not connected - message will not be sent immediately. "
             "If this problem does not resolve itself - "
             "check your firewall settings",
             "with invalid state proof from"]


def testFaberCreateLink(faberLinkAdded):
    pass


def test_alice_loads_faber_request(alice_faber_request_loaded):
    pass


def test_alice_syncs_faber_request_link(alice_faber_request_link_synced):
    pass


def testFaberAdded(faberAdded):
    pass


def testAliceAgentConnected(faberAdded, aliceAgentConnected):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def test_alice_accept_faber_request(aliceAcceptedFaber):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def test_alice_accept_acme_request(aliceAcceptedAcme):
    pass


@pytest.mark.skip(reason="SOV-562. Not yet implemented")
def testAddSchema():
    raise NotImplementedError


@pytest.mark.skip(reason="SOV-562. Not yet implemented")
def testAddClaimDefs():
    raise NotImplementedError


@pytest.mark.skip(reason="SOV-563. Incomplete implementation")
def testMultipleAcceptance(aliceAcceptedFaber,
                           faberIsRunning,
                           faberLinkAdded,
                           faberAdded,
                           walletBuilder,
                           agentBuilder,
                           emptyLooper,
                           faberNonceForAlice):
    """
    For the test agent, Faber. Any invite nonce is acceptable.
    """
    faberAgent, _ = faberIsRunning
    assert len(faberAgent.wallet._connections) == 1
    link = next(faberAgent.wallet._connections.values())
    wallet = walletBuilder("Bob")
    otherAgent = agentBuilder(wallet)
    emptyLooper.add(otherAgent)

    check_accept_request(emptyLooper,
                         nonce=faberNonceForAlice,
                         inviteeAgent=otherAgent,
                         inviterAgentAndWallet=faberIsRunning,
                         linkName=link.name)

    assert len(faberAgent.wallet._connections) == 2
