from sovrin_client.test import waits
from stp_core.loop.eventually import eventually
from anoncreds.protocol.types import SchemaKey, ID
from sovrin_client.test.agent.messages import get_claim_request_libsovrin_msg


def test_claim_request_from_libsovrin_works(aliceAgent, aliceAcceptedFaber, aliceAcceptedAcme,
                  acmeAgent, emptyLooper, faberAgent):
    faberLink = aliceAgent.wallet.getLink('Faber College')
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

        msg = get_claim_request_libsovrin_msg(claimReq, schema.seqId)

        aliceAgent.signAndSendToLink(msg=msg, linkName=faberLink.name)

    emptyLooper.run(eventually(create_claim_init_data_and_send_msg, timeout=timeout))

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaimSignature(ID(schemaKey))
        assert claim.primaryClaim

    emptyLooper.run(eventually(chkClaims, timeout=timeout))

    # 3. send proof to Acme
    acme_link, acme_proof_req = aliceAgent.wallet.getMatchingLinksWithProofReq(
        "Job-Application", "Acme Corp")[0]
    aliceAgent.sendProof(acme_link, acme_proof_req)

    # 4. check that proof is verified by Acme
    def chkProof():
        internalId = acmeAgent.get_internal_id_by_nonce(acme_link.invitationNonce)
        link = acmeAgent.wallet.getLinkBy(internalId=internalId)
        assert "Job-Application" in link.verifiedClaimProofs

    timeout = waits.expectedClaimsReceived()
    emptyLooper.run(eventually(chkProof, timeout=timeout))
