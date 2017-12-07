import os
import stat

import pytest

from plenum.common.util import randomString, normalizedWalletFileName
from plenum.test.conftest import tdirWithPoolTxns
from indy_client.agent.agent import createAgent
from indy_client.test.agent.conftest import emptyLooper, startAgent

from indy_client.test.agent.acme import create_acme as createAcmeAgent, AcmeAgent
from indy_client.test.agent.helper import buildAcmeWallet as agentWallet
from indy_client.test.cli.conftest \
    import acmeAddedByPhil as agentAddedBySponsor
from indy_client.test.cli.helper import compareAgentIssuerWallet
from indy_client.test.client.TestClient import TestClient
from stp_core.network.port_dispenser import genHa

agentPort = genHa()[1]


def getNewAgent(name, basedir, port, wallet):
    return createAcmeAgent(name, wallet, base_dir_path=basedir, port=port)


def runAgent(looper, basedir, port, name=None, agent=None):
    wallet = agentWallet()
    wallet.name = name
    name = name or "Agent" + randomString(5)
    agent = agent or getNewAgent(name, basedir, port, wallet)
    return startAgent(looper, agent, wallet)


def _startAgent(looper, base_dir, port, name):
    agent, wallet = runAgent(looper, base_dir, port, name)
    return agent, wallet


@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithClientPoolTxns):
    return _startAgent(emptyLooper, tdirWithClientPoolTxns, agentPort, "Agent0")


def changeAndPersistWallet(agent, emptyLooper):
    walletName = normalizedWalletFileName(agent._wallet.name)
    expectedFilePath = os.path.join(agent.getContextDir(), walletName)
    assert "agents" in expectedFilePath
    assert agent.name.lower().replace(" ", "-") in expectedFilePath
    walletToBePersisted = agent._wallet
    walletToBePersisted.idsToSigners = {}
    agent.stop()
    emptyLooper.runFor(.5)
    assert os.path.isfile(expectedFilePath)
    assert stat.S_IMODE(os.stat(agent.getContextDir()
                                ).st_mode) == agent.config.WALLET_DIR_MODE
    assert stat.S_IMODE(
        os.stat(expectedFilePath).st_mode) == agent.config.WALLET_FILE_MODE
    return walletToBePersisted


def changePersistAndRestoreWallet(agent, emptyLooper):
    assert agent
    changeAndPersistWallet(agent, emptyLooper)
    agent.start(emptyLooper)
    assert agent._wallet.idsToSigners == {}


def testAgentPersistsWalletWhenStopped(poolNodesStarted, emptyLooper,
                                       agentAddedBySponsor, agentStarted):
    agent, _ = agentStarted
    changePersistAndRestoreWallet(agent, emptyLooper)


def testAgentUsesRestoredWalletIfItHas(
        poolNodesStarted, emptyLooper, tdirWithClientPoolTxns,
        agentAddedBySponsor, agentStarted):
    agent, wallet = agentStarted
    changeAndPersistWallet(agent, emptyLooper)

    newAgent = getNewAgent(agent.name, tdirWithClientPoolTxns, agentPort,
                           agentWallet())
    assert newAgent._wallet.idsToSigners == {}


def testAgentCreatesWalletIfItDoesntHaveOne(tdirWithClientPoolTxns):
    agent = createAgent(AcmeAgent, "Acme Corp",
                        wallet=None, basedirpath=tdirWithClientPoolTxns,
                        port=genHa()[1], clientClass=TestClient)
    assert agent._wallet is not None


def testAgentWalletRestoration(poolNodesStarted, tdirWithClientPoolTxns, emptyLooper,
                               agentAddedBySponsor, agentStarted):
    agent, wallet = agentStarted
    unpersistedIssuerWallet = agent.issuer.wallet
    agent.stop()
    emptyLooper.removeProdable(agent)
    newAgent, newWallet = _startAgent(emptyLooper, tdirWithClientPoolTxns,
                                      agentPort, "Agent0")
    restoredIssuerWallet = newAgent.issuer.wallet
    compareAgentIssuerWallet(unpersistedIssuerWallet, restoredIssuerWallet)
