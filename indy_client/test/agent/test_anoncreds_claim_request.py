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
from anoncreds.protocol.types import SchemaKey, ID
from indy_client.test.agent.messages import get_claim_request_libindy_msg


def test_claim_request_from_libindy_works(
        aliceAgent,
        aliceAcceptedFaber,
        aliceAcceptedAcme,
        acmeAgent,
        emptyLooper,
        faberAgent):
    faberLink = aliceAgent.wallet.getConnection('Faber College')
    name, version, origin = faberLink.availableClaims[0]
    schemaKey = SchemaKey(name, version, origin)
    timeout = waits.expectedClaimsReceived()

    schema = faberAgent.issuer.wallet._schemasByKey[schemaKey]

    async def create_claim_init_data_and_send_msg():
        claimReq = await aliceAgent.prover.createClaimRequest(
            schemaId=ID(schemaKey),
            proverId='b1134a647eb818069c089e7694f63e6d',
            reqNonRevoc=False)

        assert claimReq

        msg = get_claim_request_libindy_msg(claimReq, schema.seqId)

        aliceAgent.signAndSendToLink(msg=msg, linkName=faberLink.name)

    emptyLooper.run(eventually(
        create_claim_init_data_and_send_msg, timeout=timeout))

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaimSignature(ID(schemaKey))
        assert claim.primaryClaim

    emptyLooper.run(eventually(chkClaims, timeout=timeout))

    # 3. send proof to Acme
    acme_link, acme_proof_req = aliceAgent.wallet.getMatchingConnectionsWithProofReq(
        "Job-Application", "Acme Corp")[0]
    aliceAgent.sendProof(acme_link, acme_proof_req)

    # 4. check that proof is verified by Acme
    def chkProof():
        internalId = acmeAgent.get_internal_id_by_nonce(
            acme_link.request_nonce)
        link = acmeAgent.wallet.getConnectionBy(internalId=internalId)
        assert "Job-Application" in link.verifiedClaimProofs

    timeout = waits.expectedClaimsReceived()
    emptyLooper.run(eventually(chkProof, timeout=timeout))
