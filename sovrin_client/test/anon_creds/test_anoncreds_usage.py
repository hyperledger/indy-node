import pytest

from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import ID, PredicateGE, AttributeInfo, ProofRequest
from sovrin_client.anon_creds.sovrin_issuer import SovrinIssuer
from sovrin_client.anon_creds.sovrin_prover import SovrinProver
from sovrin_client.anon_creds.sovrin_verifier import SovrinVerifier
from sovrin_client.test.anon_creds.conftest import GVT


@pytest.fixture(scope="module")
def attrRepo():
    return AttributeRepoInMemory()


@pytest.fixture(scope="module")
def issuer(steward, stewardWallet, attrRepo):
    return SovrinIssuer(steward, stewardWallet, attrRepo)


@pytest.fixture(scope="module")
def prover(userClientA, userWalletA):
    return SovrinProver(userClientA, userWalletA)


@pytest.fixture(scope="module")
def verifier(userClientB, userWalletB):
    return SovrinVerifier(userClientB, userWalletB)


def testAnonCredsPrimaryOnly(issuer, prover, verifier, attrRepo, primes1, looper):
    async def doTestAnonCredsPrimaryOnly():
        # 1. Create a Schema
        schema = await issuer.genSchema('GVT', '1.0', GVT.attribNames())
        schemaId = ID(schemaKey=schema.getKey(), schemaId=schema.seqId)

        # 2. Create keys for the Schema
        await issuer.genKeys(schemaId, **primes1)

        # 3. Issue accumulator
        #TODO: Not implemented yet
        #await issuer.issueAccumulator(schemaId=schemaId, iA='110', L=5)

        # 4. set attributes for user1
        attrs = GVT.attribs(name='Alex', age=28, height=175, sex='male')
        proverId = str(prover.proverId)
        attrRepo.addAttributes(schema.getKey(), proverId, attrs)

        # 5. request Claims
        claimsReq = await prover.createClaimRequest(schemaId, proverId, False)
        (claim_signature, claim_attributes) = await issuer.issueClaim(schemaId, claimsReq)
        await prover.processClaim(schemaId, claim_attributes, claim_signature)

        # 6. proof Claims
        proofRequest = ProofRequest("proof1", "1.0", verifier.generateNonce(),
                                    verifiableAttributes={'attr_uuid': AttributeInfo('name', schema.seqId)},
                                    predicates={'predicate_uuid': PredicateGE('age', 18)})

        proof = await prover.presentProof(proofRequest)
        assert proof.requestedProof.revealed_attrs['attr_uuid'][1] == 'Alex'
        assert await verifier.verify(proofRequest, proof)

    looper.run(doTestAnonCredsPrimaryOnly)
