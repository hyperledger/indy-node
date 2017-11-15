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

from plenum.common.startable import Status
from pytest import fixture

from indy_client.agent.agent import Agent


@fixture(scope="module")
def agent(tdir):
    return Agent('agent1', tdir)


@fixture(scope="module")
def startedAgent(emptyLooper, agent):
    emptyLooper.add(agent)
    return agent


def testStartup(startedAgent, emptyLooper):
    assert startedAgent.isGoing() is True
    assert startedAgent.get_status() is Status.starting
    emptyLooper.runFor(.1)
    assert startedAgent.get_status() is Status.started


def testShutdown(startedAgent):
    startedAgent.stop()
    assert startedAgent.isGoing() is False
    assert startedAgent.get_status() is Status.stopped
