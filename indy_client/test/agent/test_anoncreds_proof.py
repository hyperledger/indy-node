from indy_client.test import waits
from stp_core.loop.eventually import eventually
from anoncreds.protocol.types import SchemaKey, ID, ProofRequest
from indy_client.test.agent.messages import get_proof_libindy_msg


def test_proof_from_libindy_works(
        aliceAgent,
        aliceAcceptedFaber,
        aliceAcceptedAcme,
        acmeAgent,
        emptyLooper,
        faberAgent):
    # 1. request Claims from Faber
    faberLink = aliceAgent.wallet.getConnection('Faber College')
    name, version, origin = faberLink.availableClaims[0]
    schemaKey = SchemaKey(name, version, origin)
    aliceAgent.sendReqClaim(faberLink, schemaKey)

    schema = faberAgent.issuer.wallet._schemasByKey[schemaKey]

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaimSignature(ID(schemaKey))
        assert claim.primaryClaim

    timeout = waits.expectedClaimsReceived()
    emptyLooper.run(eventually(chkClaims, timeout=timeout))

    # 3. send proof to Acme
    acme_link, acme_proof_req = aliceAgent.wallet.getMatchingConnectionsWithProofReq(
        "Job-Application", "Acme Corp")[0]

    async def create_proof():
        proofRequest = ProofRequest("proof1",
                                    "1.0",
                                    int(acme_proof_req.nonce),
                                    verifiableAttributes=acme_proof_req.verifiableAttributes,
                                    predicates=acme_proof_req.predicates)

        proof = await  aliceAgent.prover.presentProof(proofRequest)

        msg = get_proof_libindy_msg(
            acme_link, acme_proof_req, proof, str(schema.seqId), schema.seqId)

        aliceAgent.signAndSendToLink(msg=msg, linkName=acme_link.name)

    emptyLooper.run(eventually(create_proof, timeout=timeout))

    # 4. check that proof is verified by Acme
    def chkProof():
        internalId = acmeAgent.get_internal_id_by_nonce(
            acme_link.request_nonce)
        link = acmeAgent.wallet.getConnectionBy(internalId=internalId)
        assert "Job-Application" in link.verifiedClaimProofs

    emptyLooper.run(eventually(chkProof, timeout=timeout))
