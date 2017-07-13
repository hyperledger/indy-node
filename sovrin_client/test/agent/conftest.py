from sovrin_client.test import waits

from plenum.common.signer_did import DidSigner

from sovrin_client.agent.endpoint import REndpoint
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_common.strict_types import strict_types
from stp_core.network.port_dispenser import genHa


strict_types.defaultShouldCheck = True

# def pytest_configure(config):
#     setattr(sys, '_called_from_test', True)
#
#
# def pytest_unconfigure(config):
#     delattr(sys, '_called_from_test')
#
#
import json
import os

import pytest

import sample
from stp_core.loop.looper import Looper
from plenum.common.util import randomString
from stp_core.loop.eventually import eventually
from plenum.test.helper import assertFunc
from sovrin_client.agent.walleted_agent import WalletedAgent
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.constants import ENDPOINT, TRUST_ANCHOR
from sovrin_client.test.agent.acme import create_acme, bootstrap_acme
from sovrin_client.test.agent.faber import create_faber, bootstrap_faber
from sovrin_client.test.agent.helper import ensureAgentConnected, buildFaberWallet, \
    buildAcmeWallet, buildThriftWallet, startAgent
from sovrin_client.test.agent.thrift import create_thrift
from sovrin_node.test.helper import addAttributeAndCheck
from sovrin_client.test.helper import createNym, TestClient

# noinspection PyUnresolvedReferences
from sovrin_node.test.conftest import nodeSet, updatedDomainTxnFile, \
    genesisTxns

# noinspection PyUnresolvedReferences
from plenum.test.conftest import poolTxnStewardData, poolTxnStewardNames


@pytest.fixture(scope="module")
def emptyLooper():
    with Looper() as l:
        yield l


@pytest.fixture(scope="module")
def walletBuilder():
    def _(name):
        wallet = Wallet(name)
        wallet.addIdentifier(signer=DidSigner())
        return wallet
    return _


@pytest.fixture(scope="module")
def aliceWallet(walletBuilder):
    return walletBuilder("Alice")


@pytest.fixture(scope="module")
def faberWallet():
    return buildFaberWallet()


@pytest.fixture(scope="module")
def acmeWallet():
    return buildAcmeWallet()


@pytest.fixture(scope="module")
def thriftWallet():
    return buildThriftWallet()


@pytest.fixture(scope="module")
def agentBuilder(tdirWithPoolTxns):
    def _(wallet, basedir=None):
        basedir = basedir or tdirWithPoolTxns
        _, port = genHa()
        _, clientPort = genHa()
        client = TestClient(randomString(6),
                            ha=("0.0.0.0", clientPort),
                            basedirpath=basedir)

        agent = WalletedAgent(name=wallet.name,
                              basedirpath=basedir,
                              client=client,
                              wallet=wallet,
                              port=port)

        return agent
    return _


@pytest.fixture(scope="module")
def aliceAgent(aliceWallet, agentBuilder):
    agent = agentBuilder(aliceWallet)
    return agent

@pytest.fixture(scope="module")
def aliceAdded(nodeSet, steward, stewardWallet,
               emptyLooper, aliceAgent):
    addAgent(emptyLooper, aliceAgent, steward, stewardWallet)


@pytest.fixture(scope="module")
def aliceIsRunning(emptyLooper, aliceAgent, aliceAdded):
    emptyLooper.add(aliceAgent)
    return aliceAgent


@pytest.fixture(scope="module")
def aliceAgentConnected(nodeSet,
                        aliceAgent,
                        aliceIsRunning,
                        emptyLooper):
    emptyLooper.run(
        eventually(
            assertFunc, aliceAgent.client.isReady))
    return aliceAgent


@pytest.fixture(scope="module")
def agentIpAddress():
    return "127.0.0.1"


@pytest.fixture(scope="module")
def faberAgentPort():
    return genHa()[1]


@pytest.fixture(scope="module")
def acmeAgentPort():
    return genHa()[1]


@pytest.fixture(scope="module")
def thriftAgentPort():
    return genHa()[1]


@pytest.fixture(scope="module")
def faberAgent(tdirWithPoolTxns, faberAgentPort, faberWallet):
    return create_faber(faberWallet.name, faberWallet,
                        base_dir_path=tdirWithPoolTxns,
                        port=faberAgentPort)


@pytest.fixture(scope="module")
def faberBootstrap(faberAgent):
    return bootstrap_faber(faberAgent)


@pytest.fixture(scope="module")
def acmeBootstrap(acmeAgent):
    return bootstrap_acme(acmeAgent)


@pytest.fixture(scope="module")
def faberAdded(nodeSet,
               steward,
               stewardWallet,
               emptyLooper,
               faberAgent):
    return addAgent(emptyLooper, faberAgent, steward, stewardWallet)


@pytest.fixture(scope="module")
def faberIsRunning(emptyLooper, tdirWithPoolTxns, faberWallet,
                   faberAgent, faberAdded, faberBootstrap):
    return startAgent(emptyLooper, faberAgent, faberWallet, bootstrap=faberBootstrap)


@pytest.fixture(scope="module")
def acmeAgent(tdirWithPoolTxns, acmeAgentPort, acmeWallet):
    return create_acme(acmeWallet.name, acmeWallet,
                      base_dir_path=tdirWithPoolTxns,
                      port=acmeAgentPort)


@pytest.fixture(scope="module")
def acmeAdded(nodeSet,
              steward,
              stewardWallet,
              emptyLooper,
              acmeAgent):
    return addAgent(emptyLooper, acmeAgent, steward, stewardWallet)


@pytest.fixture(scope="module")
def acmeIsRunning(emptyLooper, tdirWithPoolTxns, acmeWallet, acmeAgent,
                  acmeAdded, acmeBootstrap):
    return startAgent(emptyLooper, acmeAgent, acmeWallet, bootstrap=acmeBootstrap)


@pytest.fixture(scope="module")
def thriftAgent(tdirWithPoolTxns, thriftAgentPort, thriftWallet):
    return create_thrift(thriftWallet.name, thriftWallet,
                        base_dir_path=tdirWithPoolTxns,
                        port=thriftAgentPort)


@pytest.fixture(scope="module")
def thfiftAdded(nodeSet,
              steward,
              stewardWallet,
              emptyLooper,
              thriftAgent):
    return addAgent(emptyLooper, thriftAgent, steward, stewardWallet)


@pytest.fixture(scope="module")
def thriftIsRunning(emptyLooper, tdirWithPoolTxns, thriftWallet,
                    thriftAgent, thriftAdded):
    return startAgent(emptyLooper, thriftAgent, thriftWallet)


# TODO: Rename it, not clear whether link is added to which wallet and
# who is adding
@pytest.fixture(scope="module")
def faberLinkAdded(faberIsRunning):
    pass


@pytest.fixture(scope="module")
def acmeLinkAdded(acmeIsRunning):
    pass


@pytest.fixture(scope="module")
def faberNonceForAlice():
    return 'b1134a647eb818069c089e7694f63e6d'


@pytest.fixture(scope="module")
def acmeNonceForAlice():
    return '57fbf9dc8c8e6acde33de98c6d747b28c'


@pytest.fixture(scope="module")
def aliceAcceptedFaber(faberIsRunning, faberNonceForAlice, faberAdded,
                       aliceIsRunning, emptyLooper,
                       aliceFaberInvitationLoaded,
                       aliceFaberInvitationLinkSynced):
    """
    Faber creates a Link object, generates a link invitation file.
    Start FaberAgent
    Start AliceAgent and send a ACCEPT_INVITE to FaberAgent.
    """

    checkAcceptInvitation(emptyLooper,
                          faberNonceForAlice,
                          aliceIsRunning,
                          faberIsRunning,
                          linkName='Faber College')


@pytest.fixture(scope="module")
def faberInvitation():
    return getInvitationFile('faber-invitation.sovrin')


@pytest.fixture(scope="module")
def acmeInvitation():
    return getInvitationFile('acme-job-application.sovrin')


@pytest.fixture(scope="module")
def aliceFaberInvitationLoaded(aliceAgent, faberInvitation):
    link = agentInvitationLoaded(aliceAgent, faberInvitation)
    assert link.name == 'Faber College'
    return link


@pytest.fixture(scope="module")
def aliceFaberInvitationLinkSynced(aliceFaberInvitationLoaded,
                                   aliceAgentConnected,
                                   aliceAgent: WalletedAgent,
                                   emptyLooper,
                                   faberAdded):
    agentInvitationLinkSynced(aliceAgent,
                              aliceFaberInvitationLoaded.name,
                              emptyLooper)


@pytest.fixture(scope="module")
def aliceAcmeInvitationLoaded(aliceAgent, acmeInvitation):
    link = agentInvitationLoaded(aliceAgent, acmeInvitation)
    assert link.name == 'Acme Corp'
    return link


@pytest.fixture(scope="module")
def aliceAcmeInvitationLinkSynced(aliceAcmeInvitationLoaded,
                                  aliceAgentConnected,
                                  aliceAgent: WalletedAgent,
                                  emptyLooper,
                                  acmeAdded):
    agentInvitationLinkSynced(aliceAgent, aliceAcmeInvitationLoaded.name,
                              emptyLooper)


@pytest.fixture(scope="module")
def aliceAcceptedAcme(acmeIsRunning, acmeNonceForAlice, acmeAdded,
                      aliceIsRunning, emptyLooper,
                      aliceAcmeInvitationLinkSynced):
    """
    Faber creates a Link object, generates a link invitation file.
    Start FaberAgent
    Start AliceAgent and send a ACCEPT_INVITE to FaberAgent.
    """

    checkAcceptInvitation(emptyLooper,
                          acmeNonceForAlice,
                          aliceIsRunning,
                          acmeIsRunning,
                          linkName='Acme Corp')


def checkAcceptInvitation(emptyLooper,
                          nonce,
                          inviteeAgent: WalletedAgent,
                          inviterAgentAndWallet,
                          linkName):
    """
    Assumes link identified by linkName is already created
    """
    assert nonce
    inviterAgent, inviterWallet = inviterAgentAndWallet  # type: WalletedAgent, Wallet

    inviteeAgent.connectTo(linkName)
    inviteeAcceptanceLink = inviteeAgent.wallet.getLink(linkName,
                                                required=True)
    ensureAgentConnected(emptyLooper, inviteeAgent, inviteeAcceptanceLink)

    inviteeAgent.accept_invitation(linkName)
    internalId = inviterAgent.get_internal_id_by_nonce(nonce)

    def chk():
        assert inviteeAcceptanceLink.remoteEndPoint[1] == inviterAgent.endpoint.ha[1]
        assert inviteeAcceptanceLink.isAccepted

        link = inviterAgent.wallet.getLinkBy(internalId=internalId)
        assert link
        assert link.remoteIdentifier == inviteeAcceptanceLink.localIdentifier

    timeout = waits.expectedAcceptInvitation()
    emptyLooper.run(eventually(chk, timeout=timeout))


def addAgent(looper, agent, steward, stewardWallet):
    # 1. add Agent's NYM (by Steward)
    agentNym = agent.wallet.defaultId
    createNym(looper,
              agentNym,
              steward,
              stewardWallet,
              role=TRUST_ANCHOR,
              verkey=agent.wallet.getVerkey())

    # 2. add client to the loop
    looper.add(agent.client)

    # 3. add attribute to the Agent's NYM with endpoint information (by Agent's client)
    ep = '127.0.0.1:{}'.format(agent.port)
    attributeData = json.dumps({ENDPOINT: {'ha': ep}})

    attrib = Attribute(name='{}_endpoint'.format(agentNym),
                       origin=agentNym,
                       value=attributeData,
                       dest=agentNym,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, agent.client, agent.wallet, attrib)
    return attrib


def getInvitationFile(fileName):
    sampleDir = os.path.dirname(sample.__file__)
    return os.path.join(sampleDir, fileName)


def agentInvitationLoaded(agent, invitation):
    link = agent.loadInvitationFile(invitation)
    assert link
    return link


def agentInvitationLinkSynced(agent,
                              linkName,
                              looper):
    done = False

    def cb(reply, err):
        nonlocal done
        assert reply
        assert not err
        done = True

    def checkDone():
        assert done, 'never got reply for agent link sync'

    agent.sync(linkName, cb)
    looper.run(eventually(checkDone))

    link = agent.wallet.getLink(linkName, required=True)
    assert link
    ep = link.remoteEndPoint
    assert ep
    assert len(ep) == 2
