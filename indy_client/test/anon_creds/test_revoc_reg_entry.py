import pytest
import json
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, TYPE, VALUE
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check


@pytest.mark.skip("Check failed adding test")
@pytest.fixture(scope="module")
def send_revoc_def_entry(looper, sdk_wallet_steward, sdk_pool_handle, txnPoolNodeSet):
    data = {
        REVOC_REG_DEF_ID: randomString(50),
        TYPE: REVOC_REG_ENTRY,
        VALUE:{
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    return req


@pytest.mark.skip("Check failed adding test")
def test_revoc_entry_validation(send_revoc_def_entry):
    # 1. Send revocaton_definition
     req = send_revoc_def_entry


@pytest.mark.skip("Check failed adding test")
def test_revoc_entry_send_twice(looper, send_revoc_def_entry, sdk_pool_handle, txnPoolNodeSet):
    # 1. Send revocation definition
    req = send_revoc_def_entry
    # 2. Resend revocation definition
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)