import pytest
import json
import random
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_signed_requests
from plenum.common.util import randomString
from indy_common.constants import TXN_TYPE, DATA, REQ_METADATA, REVOC_REG_DEF, SIGNATURE_TYPE, REF
from plenum.test.conftest import sdk_pool_handle, sdk_pool_name, sdk_wallet_steward, sdk_wallet_handle, \
    sdk_wallet_name, sdk_steward_seed


@pytest.fixture(scope="module")
def send_revoc_def(public_repo, looper):#, sdk_wallet_steward, sdk_pool_handle):
    data = {
        "id": randomString(50),
        "type": 'CL_ACCUM',
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
    reqMetadata = {
        "submitterDid": randomString(50)
    }
    op = {
        TXN_TYPE: REVOC_REG_DEF,
        DATA: data,
        REQ_METADATA: reqMetadata,
        SIGNATURE_TYPE: "REV_DEF",
        REF: random.randint(10, 100000)
    }

    looper.run(public_repo._sendSubmitReq(op))
    return op
    # req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, op)
    # sdk_send_signed_requests(sdk_pool_handle, [json.dumps(req.as_dict)])


def test_revoc_validation(send_revoc_def, txnPoolNodeSet):
    # 1. Send revocaton_definition
    op = send_revoc_def

def test_revoc_send_twice(looper, public_repo, send_revoc_def, txnPoolNodeSet):
    # 1. Send revocation definition
    op = send_revoc_def
    # 2. Resend revocation definition
    looper.run(public_repo._sendSubmitReq(op))