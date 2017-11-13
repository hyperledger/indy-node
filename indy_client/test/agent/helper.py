#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import argparse
import sys

from indy_client.agent.helper import buildAgentWallet
from indy_client.test import waits
from stp_core.loop.eventually import eventually
from indy_client.agent.run_agent import runAgent
from indy_common.config_util import getConfig

config = getConfig()


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
