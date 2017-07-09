import pytest

from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import ID, ProofInput, PredicateGE
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
        claims = await issuer.issueClaim(schemaId, claimsReq)
        await prover.processClaim(schemaId, claims)

        # 6. proof Claims
        proofInput = ProofInput(
            ['name'],
            [PredicateGE('age', 18)])

        nonce = verifier.generateNonce()
        proof, revealedAttrs = await prover.presentProof(proofInput, nonce)
        assert await verifier.verify(proofInput, proof, revealedAttrs, nonce)

    looper.run(doTestAnonCredsPrimaryOnly)
