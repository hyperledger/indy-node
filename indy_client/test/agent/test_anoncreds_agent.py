from indy_client.test import waits

from stp_core.loop.eventually import eventually

from anoncreds.protocol.types import SchemaKey, ID


def testAnonCreds(aliceAgent, aliceAcceptedFaber, aliceAcceptedAcme,
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
    timeout = waits.expectedClaimsReceived()
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
