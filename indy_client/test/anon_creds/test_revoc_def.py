import pytest
import json
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_DEF
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check
from plenum.test.pool_transactions.conftest import looper


@pytest.mark.skip("Check failed adding test")
@pytest.fixture(scope="module")
def send_revoc_def(looper, sdk_wallet_steward, sdk_pool_handle, txnPoolNodeSet):
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

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    return req


@pytest.mark.skip("Check failed adding test")
def test_revoc_validation(send_revoc_def):
    # 1. Send revocaton_definition
    req = send_revoc_def


@pytest.mark.skip("Check failed adding test")
def test_revoc_send_twice(send_revoc_def, sdk_pool_handle, looper, txnPoolNodeSet):
    # 1. Send revocation definition
    req = send_revoc_def
    # 2. Resend revocation definition
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)