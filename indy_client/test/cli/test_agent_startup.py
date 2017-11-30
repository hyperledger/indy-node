import pytest

# it is fixture - do not remove
from indy_client.test.cli.conftest import acmeAddedByPhil as agentAddedBySponsor
from indy_common.exceptions import NotConnectedToNetwork

from plenum.common.exceptions import OperationError, NoConsensusYet

from stp_core.network.exceptions import PortNotAvailable
from stp_core.network.port_dispenser import genHa
from plenum.common.types import HA
from plenum.common.util import randomString
from stp_core.network.util import checkPortAvailable
from indy_client.test.agent.conftest import startAgent

from indy_client.test.agent.acme import create_acme as createAgent
from indy_client.test.agent.acme import bootstrap_acme as bootstrap_agent
from indy_client.test.agent.helper import buildAcmeWallet as agentWallet


agentPort = genHa()[1]


def getNewAgent(name, basedir, port, wallet):
    return createAgent(name, wallet, base_dir_path=basedir, port=port)


def runAgent(looper, basedir, port, name=None, agent=None):
    wallet = agentWallet()
    name = name or "Agent" + randomString(5)
    agent = agent or getNewAgent(name, basedir, port, wallet)
    agent._name = name
    return startAgent(looper, agent, wallet, bootstrap_agent(agent))


def stopAgent(looper, name):
    agent = looper.removeProdable(name=name)
    if agent:
        agent.stop()


@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithPoolTxns):
    runAgent(emptyLooper, tdirWithPoolTxns, agentPort, "Agent0")


def testCreateAgentDoesNotAllocatePort(tdirWithPoolTxns):
    for i in range(2):
        checkPortAvailable(HA("0.0.0.0", agentPort))
        agent = getNewAgent("Agent0", tdirWithPoolTxns,
                            agentPort, agentWallet())
        checkPortAvailable(HA("0.0.0.0", agentPort))
        agent.stop()


def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithClientPoolTxns):
    import indy_client.agent.run_agent
    indy_client.agent.run_agent.CONNECTION_TIMEOUT = 10
    newAgentName = "Agent2"
    with pytest.raises(NotConnectedToNetwork):
        runAgent(emptyLooper, tdirWithClientPoolTxns, agentPort,
                 name=newAgentName)
    stopAgent(emptyLooper, newAgentName)


def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithClientPoolTxns,
                                emptyLooper, agentAddedBySponsor,
                                agentStarted):
    with pytest.raises(PortNotAvailable):
        runAgent(emptyLooper, tdirWithClientPoolTxns, agentPort, name='Agent4')

    stopAgent(emptyLooper, 'Agent4')


def testStartAgentChecksForPortAvailability(poolNodesStarted, tdirWithClientPoolTxns,
                                            emptyLooper, agentAddedBySponsor):
    newAgentName1 = "Agent11"
    newAgentName2 = "Agent12"
    with pytest.raises(PortNotAvailable):
        agent = getNewAgent(newAgentName1, tdirWithClientPoolTxns, agentPort,
                            agentWallet())
        runAgent(emptyLooper, tdirWithClientPoolTxns, agentPort,
                 name=newAgentName2)
        runAgent(emptyLooper, tdirWithClientPoolTxns, agentPort,
                 name=newAgentName1, agent=agent)

    stopAgent(emptyLooper, newAgentName2)
