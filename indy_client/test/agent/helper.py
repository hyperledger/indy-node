import argparse
import sys

from indy_client.agent.helper import buildAgentWallet
from indy_client.test import waits
from stp_core.loop.eventually import eventually
from indy_client.agent.run_agent import runAgent


def connectAgents(agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    e1.connectTo(e2.ha)


def ensureAgentConnected(looper, agent, link):
    linkHa = link.getRemoteEndpoint(required=True)

    def _checkConnected():
        assert agent.endpoint.isConnectedTo(ha=linkHa)

    timeout = waits.expectedAgentConnected()
    looper.run(eventually(_checkConnected, timeout=timeout))


def getAgentCmdLineParams():
    if sys.stdin.isatty():
        parser = argparse.ArgumentParser(
            description="Starts agents with given port, cred def and issuer seq")

        parser.add_argument('--port', required=False,
                            help='port where agent will listen')

        parser.add_argument('--withcli',
                            help='if given, agent will start in cli mode',
                            action='store_true')

        args = parser.parse_args()
        port = int(args.port) if args.port else None
        with_cli = args.withcli
        return port, with_cli
    else:
        return None, False


def buildFaberWallet():
    return buildAgentWallet(
        "FaberCollege", b'Faber000000000000000000000000000')


def buildAcmeWallet():
    return buildAgentWallet("AcmeCorp", b'Acme0000000000000000000000000000')


def buildThriftWallet():
    return buildAgentWallet("ThriftBank", b'Thrift00000000000000000000000000')


def startAgent(looper, agent, wallet, bootstrap=None):
    agent = agent
    wallet.pendSyncRequests()
    prepared = wallet.preparePending()
    agent.client.submitReqs(*prepared)

    runAgent(agent, looper, bootstrap=bootstrap)
    return agent, wallet
