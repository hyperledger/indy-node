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

from indy_client.test import waits
from stp_core.loop.eventually import eventually
from plenum.test.testable import spy, SpyLog

from indy_client.agent.constants import PING, PONG

whitelist = ["is not connected - message will not be sent immediately.If this problem does not resolve itself - check your firewall settings"]


def testPing(aliceAcceptedFaber, faberIsRunning, aliceAgent, emptyLooper):
    faberAgent, _ = faberIsRunning

    faber_log = SpyLog()
    alice_log = SpyLog()
    faberAgent.msgHandlers[PING] = spy(
        faberAgent._handlePing, False, True, spy_log=faber_log)
    aliceAgent.msgHandlers[PONG] = spy(
        aliceAgent._handlePong, False, True, spy_log=alice_log)

    recvd_pings = 0
    recvd_pongs = 0
    aliceAgent.sendPing('Faber College')

    def chk():
        assert (recvd_pings + 1) == faber_log.count(
            faberAgent._handlePing.__name__)
        assert (recvd_pongs + 1) == alice_log.count(
            aliceAgent._handlePong.__name__)

    timeout = waits.expectedAgentPing()
    emptyLooper.run(eventually(chk, retryWait=1, timeout=timeout))
