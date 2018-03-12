import pytest
from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import AttribType, AttribDef, Schema, ID
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory

from indy_client.anon_creds.indy_public_repo import IndyPublicRepo

GVT = AttribDef('gvt',
                [AttribType('name', encode=True),
                 AttribType('age', encode=False),
                 AttribType('height', encode=False),
                 AttribType('sex', encode=True)])

# We perform all tests twice:
# - no revocation case (primary key only)
# - revocation case (both primary and revocation keys)
# There are two Schemas generated (one for each branch of tests)
revoc_params = ['revocation', 'no_revocation']


@pytest.fixture(scope="module")
def public_repo(steward, stewardWallet):
    return IndyPublicRepo(steward, stewardWallet)


@pytest.fixture(scope="module")
def public_repo_2(trustee, trusteeWallet):
    return IndyPublicRepo(trustee, trusteeWallet)


@pytest.fixture(scope="module")
def public_repo_for_client(client1, added_client_without_role):
    return IndyPublicRepo(client1, added_client_without_role)


@pytest.fixture(scope="module")
def issuer(public_repo):
    return Issuer(IssuerWalletInMemory('issuer1', public_repo),
                  AttributeRepoInMemory())


@pytest.fixture(scope="module", params=revoc_params)
def schema(request, stewardWallet):
    return Schema(name='GVT',
                  version='1.0' if request.param == 'revocation' else '2.0',
                  attrNames=GVT.attribNames(),
                  issuerId=stewardWallet.defaultId,
                  seqId=None)


@pytest.fixture(scope="module")
def submitted_schema(public_repo, schema, looper):
    return looper.run(public_repo.submitSchema(schema))


@pytest.fixture(scope="module")
def submitted_schema_ID(submitted_schema):
    return ID(schemaKey=submitted_schema.getKey(),
              schemaId=submitted_schema.seqId)


@pytest.fixture(scope="module")
def public_secret_key(submitted_schema_ID, issuer, primes1, looper):
    return looper.run(
        issuer._primaryIssuer.genKeys(submitted_schema_ID, **primes1))


@pytest.fixture(scope="module")
def public_secret_revocation_key(issuer, looper, schema):
    if schema.version == '2.0':
        return (None, None)
    return looper.run(issuer._nonRevocationIssuer.genRevocationKeys())


@pytest.fixture(scope="module")
def public_key(public_secret_key):
    return public_secret_key[0]


@pytest.fixture(scope="module")
def public_revocation_key(public_secret_revocation_key):
    return public_secret_revocation_key[0]


@pytest.fixture(scope="module")
def submitted_claim_def(submitted_schema_ID, public_repo, public_secret_key,
                        public_secret_revocation_key, looper):
    pk, sk = public_secret_key
    pkR, skR = public_secret_revocation_key
    return looper.run(public_repo.submitPublicKeys(id=submitted_schema_ID,
                                                   pk=pk,
                                                   pkR=pkR,
                                                   signatureType='CL'))


@pytest.fixture(scope="module")
def submitted_public_key(submitted_claim_def):
    return submitted_claim_def[0]


@pytest.fixture(scope="module")
def submitted_public_revocation_key(submitted_claim_def):
    return submitted_claim_def[1]
