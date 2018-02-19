import pytest
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_DEF


@pytest.mark.skip("Check failed adding test")
@pytest.fixture(scope="module")
def send_revoc_def(public_repo, looper):
    data = {
        "id": randomString(50),
        "type": REVOC_REG_DEF,
        "tag": randomString(5),
        "credDefId": randomString(50),
        "value":{
            "issuanceType": "issuance type",
            "maxCredNum": 1000000,
            "tailsHash": randomString(50),
            "tailsLocation": 'http://tails.location.com',
            "publicKeys": {},
        }
    }

    looper.run(public_repo._sendSubmitReq(data))
    return data


@pytest.mark.skip("Check failed adding test")
def test_revoc_validation(send_revoc_def):
    # 1. Send revocaton_definition
    op = send_revoc_def


@pytest.mark.skip("Check failed adding test")
def test_revoc_send_twice(looper, public_repo, send_revoc_def):
    # 1. Send revocation definition
    op = send_revoc_def
    # 2. Resend revocation definition
    looper.run(public_repo._sendSubmitReq(op))
