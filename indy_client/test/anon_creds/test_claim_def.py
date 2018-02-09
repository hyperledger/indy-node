import random
import sys

import pytest

from plenum.common.exceptions import OperationError
from stp_core.common.log import getlogger

logger = getlogger()


def test_submit_claim_def(submitted_claim_def):
    assert submitted_claim_def


def test_submit_claim_def_same_schema_and_signature_type(submitted_claim_def,
                                                         looper, public_repo,
                                                         submitted_schema_ID,
                                                         public_key, public_revocation_key):
    assert submitted_claim_def
    with pytest.raises(OperationError) as ex_info:
        looper.run(public_repo.submitPublicKeys(id=submitted_schema_ID,
                                                pk=public_key,
                                                pkR=public_revocation_key,
                                                signatureType='CL'))
        ex_info.match("can have one and only one CLAIM_DEF")


def test_submit_claim_def_same_schema_different_signature_type(
        submitted_claim_def,
        looper, public_repo,
        submitted_schema_ID,
        public_key, public_revocation_key):
    assert submitted_claim_def
    looper.run(public_repo.submitPublicKeys(id=submitted_schema_ID,
                                            pk=public_key,
                                            pkR=public_revocation_key,
                                            signatureType='CL2'))


def test_submit_same_claim_def_by_different_issuer(
        submitted_claim_def,
        looper, public_repo_2,
        submitted_schema_ID,
        public_key, public_revocation_key):
    assert submitted_claim_def
    looper.run(public_repo_2.submitPublicKeys(id=submitted_schema_ID,
                                              pk=public_key,
                                              pkR=public_revocation_key,
                                              signatureType='CL'))


def test_get_primary_public_key(submitted_schema_ID, submitted_public_key,
                                public_repo, looper):
    pk = looper.run(public_repo.getPublicKey(id=submitted_schema_ID,
                                             signatureType='CL'))
    assert pk == submitted_public_key


def test_get_primary_public_key_non_existent(submitted_schema_ID,
                                             public_repo, looper):
    schemaId = submitted_schema_ID._replace(
        schemaId=random.randint(100, 300))
    with pytest.raises(ValueError):
        looper.run(public_repo.getPublicKey(id=schemaId, signatureType='CL'))


def test_get_revocation_public_key(submitted_schema_ID,
                                   submitted_public_revocation_key,
                                   public_repo, looper):
    pk = looper.run(
        public_repo.getPublicKeyRevocation(id=submitted_schema_ID,
                                           signatureType='CL'))

    if sys.platform == 'win32':
        assert pk
        logger.warning("Gotten public revocation key is not verified "
                       "on Windows for matching against submitted public "
                       "revocation key since they are different on Windows "
                       "due to an issue in charm-crypto package.")
    else:
        assert pk == submitted_public_revocation_key


def test_get_revocation_public_key_non_existent(submitted_schema_ID,
                                                public_repo, looper):
    schemaId = submitted_schema_ID._replace(
        schemaId=random.randint(100, 300))
    with pytest.raises(ValueError):
        looper.run(public_repo.getPublicKeyRevocation(id=schemaId,
                                                      signatureType='CL'))
