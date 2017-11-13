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

from plenum.test import waits
from indy_client.test.helper import checkRejects, checkNacks
from indy_common.constants import NULL
from indy_common.identity import Identity
from stp_core.loop.eventually import eventually


def sendIdentityRequest(actingClient, actingWallet, idy):
    idr = idy.identifier
    if actingWallet.getTrustAnchoredIdentity(idr):
        actingWallet.updateTrustAnchoredIdentity(idy)
    else:
        actingWallet.addTrustAnchoredIdentity(idy)
    reqs = actingWallet.preparePending()
    actingClient.submitReqs(*reqs)
    return reqs


def sendChangeVerkey(actingClient, actingWallet, idr, verkey):
    idy = Identity(identifier=idr, verkey=verkey)
    return sendIdentityRequest(actingClient, actingWallet, idy)


def sendSuspendRole(actingClient, actingWallet, did):
    idy = Identity(identifier=did, role=NULL)
    return sendIdentityRequest(actingClient, actingWallet, idy)


def checkIdentityRequestFailed(looper, client, req, cause):
    timeout = waits.expectedReqRejectQuorumTime()
    # TODO: Just for now, better to have a generic negative response checker
    try:
        looper.run(eventually(checkRejects,
                              client,
                              req.reqId,
                              cause, retryWait=1, timeout=timeout))
    except AssertionError:
        looper.run(eventually(checkNacks,
                              client,
                              req.reqId,
                              cause, retryWait=1, timeout=timeout))


def checkIdentityRequestSucceed(looper, actingClient, actingWallet, idr):
    def chk():
        assert actingWallet.getTrustAnchoredIdentity(idr).seqNo is not None
    timeout = waits.expectedTransactionExecutionTime(
        len(actingClient.nodeReg)
    )
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def changeVerkey(looper, actingClient, actingWallet, idr, verkey,
                 nAckReasonContains=None):
    reqs = sendChangeVerkey(actingClient, actingWallet, idr, verkey)
    if not nAckReasonContains:
        checkIdentityRequestSucceed(looper, actingClient, actingWallet, idr)
    else:
        checkIdentityRequestFailed(
            looper, actingClient, reqs[0], nAckReasonContains)


def suspendRole(looper, actingClient, actingWallet,
                idr, nAckReasonContains=None):
    reqs = sendSuspendRole(actingClient, actingWallet, idr)
    if not nAckReasonContains:
        checkIdentityRequestSucceed(looper, actingClient, actingWallet, idr)
    else:
        checkIdentityRequestFailed(
            looper, actingClient, reqs[0], nAckReasonContains)
