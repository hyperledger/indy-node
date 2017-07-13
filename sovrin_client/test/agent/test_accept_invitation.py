import logging

import pytest

from sovrin_client.test.agent.conftest import checkAcceptInvitation

concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]

whitelist = ["is not connected - message will not be sent immediately.If this problem does not resolve itself - check your firewall settings"]

def testFaberCreateLink(faberLinkAdded):
    pass


def testAliceLoadsFaberInvitation(aliceFaberInvitationLoaded):
    pass


def testAliceSyncsFaberInvitationLink(aliceFaberInvitationLinkSynced):
    pass


def testFaberAdded(faberAdded):
    pass


def testAliceAgentConnected(faberAdded, aliceAgentConnected):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def testAliceAcceptFaberInvitation(aliceAcceptedFaber):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def testAliceAcceptAcmeInvitation(aliceAcceptedAcme):
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
    assert len(faberAgent.wallet._links) == 1
    link = next(faberAgent.wallet._links.values())
    wallet = walletBuilder("Bob")
    otherAgent = agentBuilder(wallet)
    emptyLooper.add(otherAgent)

    checkAcceptInvitation(emptyLooper,
                          nonce=faberNonceForAlice,
                          inviteeAgent=otherAgent,
                          inviterAgentAndWallet=faberIsRunning,
                          linkName=link.name)

    assert len(faberAgent.wallet._links) == 2
