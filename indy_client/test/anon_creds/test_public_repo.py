import random
import sys

import pytest

from anoncreds.protocol.exceptions import SchemaNotFoundError
from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import Schema, ID
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory
from plenum.common.util import randomString
from stp_core.common.log import getlogger

from indy_client.anon_creds.indy_public_repo import IndyPublicRepo
from indy_client.test.anon_creds.conftest import GVT
from random import randint

logger = getlogger()


@pytest.fixture(scope="module")
def publicRepo(steward, stewardWallet):
    return IndyPublicRepo(steward, stewardWallet)


@pytest.fixture(scope="module")
def issuerGvt(publicRepo):
    return Issuer(IssuerWalletInMemory('issuer1', publicRepo),
                  AttributeRepoInMemory())


@pytest.fixture(scope="module")
def schemaDefGvt(stewardWallet):
    return Schema(name='GVT',
                  version='1.0',
                  attrNames=GVT.attribNames(),
                  issuerId=stewardWallet.defaultId,
                  seqId=None)


@pytest.fixture(scope="module")
def schemaDefGvt2(stewardWallet):
    return Schema(name='GVT',
                  version='2.0',
                  attrNames=GVT.attribNames(),
                  issuerId=stewardWallet.defaultId,
                  seqId=None)


@pytest.fixture(scope="module")
def submittedSchemaDefGvt(publicRepo, schemaDefGvt, looper):
    return looper.run(publicRepo.submitSchema(schemaDefGvt))


@pytest.fixture(scope="module")
def submittedSchemaDefGvt2(publicRepo, schemaDefGvt2, looper):
    return looper.run(publicRepo.submitSchema(schemaDefGvt2))


@pytest.fixture(scope="module")
def submittedSchemaDefGvtID(submittedSchemaDefGvt):
    return ID(schemaKey=submittedSchemaDefGvt.getKey(),
              schemaId=submittedSchemaDefGvt.seqId)


@pytest.fixture(scope="module")
def submittedSchemaDefGvtID2(submittedSchemaDefGvt2):
    return ID(schemaKey=submittedSchemaDefGvt2.getKey(),
              schemaId=submittedSchemaDefGvt2.seqId)


@pytest.fixture(scope="module")
def publicSecretKey(submittedSchemaDefGvtID, issuerGvt, primes1, looper):
    return looper.run(
        issuerGvt._primaryIssuer.genKeys(submittedSchemaDefGvtID, **primes1))


@pytest.fixture(scope="module")
def publicSecretKey2(submittedSchemaDefGvtID2, issuerGvt, primes2, looper):
    return looper.run(
        issuerGvt._primaryIssuer.genKeys(submittedSchemaDefGvtID2, **primes2))


@pytest.fixture(scope="module")
def publicSecretRevocationKey(issuerGvt, looper):
    return looper.run(issuerGvt._nonRevocationIssuer.genRevocationKeys())


@pytest.fixture(scope="module")
def publicKey(publicSecretKey):
    return publicSecretKey[0]


@pytest.fixture(scope="module")
def publicKey2(publicSecretKey2):
    return publicSecretKey2[0]


@pytest.fixture(scope="module")
def publicRevocationKey(publicSecretRevocationKey):
    return publicSecretRevocationKey[0]


@pytest.fixture(scope="module")
def submittedPublicKeys(submittedSchemaDefGvtID, publicRepo, publicSecretKey,
                        publicSecretRevocationKey, looper):
    pk, sk = publicSecretKey
    pkR, skR = publicSecretRevocationKey
    return looper.run(publicRepo.submitPublicKeys(id=submittedSchemaDefGvtID,
                                                  pk=pk,
                                                  pkR=pkR,
                                                  signatureType='CL'))


@pytest.fixture(scope="module")
def submittedPublicKeysNoRevocation(submittedSchemaDefGvtID2, publicRepo, publicKey2,
                                    looper):
    return looper.run(publicRepo.submitPublicKeys(id=submittedSchemaDefGvtID2,
                                                  pk=publicKey2,
                                                  pkR=None,
                                                  signatureType='CL'))


@pytest.fixture(scope="module")
def submittedPublicKeyNoRevocation(submittedPublicKeysNoRevocation):
    return submittedPublicKeysNoRevocation[0]


@pytest.fixture(scope="module")
def submittedPublicKey(submittedPublicKeys):
    return submittedPublicKeys[0]


@pytest.fixture(scope="module")
def submittedPublicRevocationKey(submittedPublicKeys):
    return submittedPublicKeys[1]


def testSubmitSchema(submittedSchemaDefGvt, schemaDefGvt):
    assert submittedSchemaDefGvt
    assert submittedSchemaDefGvt.seqId

    # initial schema has stub seqno - excluding seqno from comparison
    def withNoSeqId(schema):
        return schema._replace(seqId=None)

    assert withNoSeqId(submittedSchemaDefGvt) == withNoSeqId(schemaDefGvt)


def testGetSchema(submittedSchemaDefGvt, publicRepo, looper):
    key = submittedSchemaDefGvt.getKey()
    schema = looper.run(publicRepo.getSchema(ID(schemaKey=key)))
    assert schema == submittedSchemaDefGvt


def testGetSchemaBySeqNo(submittedSchemaDefGvt, publicRepo, looper):
    schema = looper.run(publicRepo.getSchema(
        ID(schemaId=submittedSchemaDefGvt.seqId)))
    assert schema == submittedSchemaDefGvt


def testGetSchemaByInvalidSeqNo(submittedSchemaDefGvt, publicRepo, looper):
    with pytest.raises(SchemaNotFoundError):
        looper.run(publicRepo.getSchema(
            ID(schemaId=(submittedSchemaDefGvt.seqId + randint(100, 1000)))))


def testGetSchemaNonExistent(submittedSchemaDefGvt, publicRepo, looper):
    key = submittedSchemaDefGvt.getKey()
    key = key._replace(name=key.name + randomString(5))
    with pytest.raises(SchemaNotFoundError):
        looper.run(publicRepo.getSchema(ID(schemaKey=key)))


def test_submit_public_key_no_revocation(submittedPublicKeysNoRevocation):
    assert submittedPublicKeysNoRevocation


def test_get_primary_public_key_no_revocation(submittedSchemaDefGvtID2,
                                              submittedPublicKeyNoRevocation,
                                              publicRepo, looper):
    pk = looper.run(publicRepo.getPublicKey(id=submittedSchemaDefGvtID2,
                                            signatureType='CL'))
    assert pk == submittedPublicKeyNoRevocation


def test_get_primary_public_key_not_existent_no_revocation(submittedSchemaDefGvtID2,
                                                           submittedPublicKeysNoRevocation,
                                                           publicRepo, looper):
    schemaId = submittedSchemaDefGvtID2._replace(
        schemaId=random.randint(100, 300))
    with pytest.raises(ValueError):
        looper.run(publicRepo.getPublicKey(id=schemaId, signatureType='CL'))


def test_get_revocation_public_key_no_revocation(submittedSchemaDefGvtID2,
                                                 submittedPublicKeysNoRevocation,
                                                 publicRepo, looper):
    pk_revoc = looper.run(publicRepo.getPublicKeyRevocation(id=submittedSchemaDefGvtID2,
                                                            signatureType='CL'))
    assert pk_revoc is None


def testSubmitPublicKey(submittedPublicKeys):
    assert submittedPublicKeys


def testGetPrimaryPublicKey(submittedSchemaDefGvtID, submittedPublicKey,
                            publicRepo, looper):
    pk = looper.run(publicRepo.getPublicKey(id=submittedSchemaDefGvtID,
                                            signatureType='CL'))
    assert pk == submittedPublicKey


def testGetPrimaryPublicKeyNonExistent(submittedSchemaDefGvtID,
                                       publicRepo, looper):
    schemaId = submittedSchemaDefGvtID._replace(
        schemaId=random.randint(100, 300))
    with pytest.raises(ValueError):
        looper.run(publicRepo.getPublicKey(id=schemaId, signatureType='CL'))


def testGetRevocationPublicKey(submittedSchemaDefGvtID,
                               submittedPublicRevocationKey,
                               publicRepo, looper):
    pk = looper.run(
        publicRepo.getPublicKeyRevocation(id=submittedSchemaDefGvtID,
                                          signatureType='CL'))

    if sys.platform == 'win32':
        assert pk
        logger.warning("Gotten public revocation key is not verified "
                       "on Windows for matching against submitted public "
                       "revocation key since they are different on Windows "
                       "due to an issue in charm-crypto package.")
    else:
        assert pk == submittedPublicRevocationKey


def testGetRevocationPublicKeyNonExistent(submittedSchemaDefGvtID,
                                          publicRepo, looper):
    schemaId = submittedSchemaDefGvtID._replace(
        schemaId=random.randint(100, 300))
    with pytest.raises(ValueError):
        looper.run(publicRepo.getPublicKeyRevocation(id=schemaId,
                                                     signatureType='CL'))
