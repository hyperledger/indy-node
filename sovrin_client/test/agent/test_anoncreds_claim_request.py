from sovrin_client.test import waits
from stp_core.loop.eventually import eventually
from anoncreds.protocol.types import SchemaKey, ID
from anoncreds.protocol.utils import crypto_int_to_str


def test_claim_request_from_libsovrin_works(aliceAgent, aliceAcceptedFaber, aliceAcceptedAcme,
                  acmeAgent, emptyLooper):
    faberLink = aliceAgent.wallet.getLink('Faber College')
    name, version, origin = faberLink.availableClaims[0]
    schemaKey = SchemaKey(name, version, origin)
    timeout = waits.expectedClaimsReceived()

    async def create_claim_init_data_and_send_msg():
        claimReq = await aliceAgent.prover.createClaimRequest(
            schemaId=ID(schemaKey),
            proverId='b1134a647eb818069c089e7694f63e6d',
            reqNonRevoc=False)

        assert claimReq

        msg = (
            {
                'issuer_did': 'FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB',
                'claim_def_seq_no': 14,
                'blinded_ms': {
                    'prover_did': 'b1134a647eb818069c089e7694f63e6d',
                    'u': str(crypto_int_to_str(claimReq.U)),
                    'ur': None
                },
                'type': 'CLAIM_REQUEST',
                'schema_seq_no': 13,
                'nonce': 'b1134a647eb818069c089e7694f63e6d',
            }
        )

        aliceAgent.signAndSendToLink(msg=msg, linkName=faberLink.name)

    emptyLooper.run(eventually(create_claim_init_data_and_send_msg, timeout=timeout))

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaims(ID(schemaKey))
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
