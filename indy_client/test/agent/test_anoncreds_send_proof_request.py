from indy_client.test import waits
from stp_core.loop.eventually import eventually
from anoncreds.protocol.types import SchemaKey, ID


def test_send_proof_works(aliceAgent, aliceAcceptedFaber, aliceAcceptedAcme,
                          acmeAgent, emptyLooper):
    # 1. request Claims from Faber
    faberLink = aliceAgent.wallet.getConnection('Faber College')
    name, version, origin = faberLink.availableClaims[0]
    schemaKey = SchemaKey(name, version, origin)
    aliceAgent.sendReqClaim(faberLink, schemaKey)

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaimSignature(ID(schemaKey))
        assert claim.primaryClaim

    emptyLooper.run(eventually(
        chkClaims, timeout=waits.expectedClaimsReceived()))

    # 3. send Proof Request to Alice
    alice_link = acmeAgent.wallet.getConnection('Alice')
    acmeAgent.sendProofReq(alice_link, 'Job-Application-v0.3')

    def chkProofRequest():
        assert len(aliceAgent.wallet.getMatchingConnectionsWithProofReq(
            "Job-Application-2", "Acme Corp")) > 0

    emptyLooper.run(eventually(chkProofRequest,
                               timeout=waits.expectedClaimsReceived()))

    # 4. send proof to Acme
    acme_link, acme_proof_req = aliceAgent.wallet.getMatchingConnectionsWithProofReq(
        "Job-Application-2", "Acme Corp")[0]
    aliceAgent.sendProof(acme_link, acme_proof_req)

    # 5. check that proof is verified by Acme
    def chkProof():
        internalId = acmeAgent.get_internal_id_by_nonce(
            acme_link.request_nonce)
        link = acmeAgent.wallet.getConnectionBy(internalId=internalId)
        assert "Job-Application-2" in link.verifiedClaimProofs

    emptyLooper.run(eventually(
        chkProof, timeout=waits.expectedClaimsReceived()))
