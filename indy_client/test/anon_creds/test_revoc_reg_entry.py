import pytest
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, TYPE, VALUE

@pytest.fixture(scope="module")
def send_revoc_def_entry(public_repo, looper):
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

    looper.run(public_repo._sendSubmitReq(data))
    return data


def test_revoc_entry_validation(send_revoc_def_entry):
    # 1. Send revocaton_definition
     op = send_revoc_def_entry

def test_revoc_entry_send_twice(looper, public_repo, send_revoc_def_entry):
    # 1. Send revocation definition
    op = send_revoc_def_entry
    # 2. Resend revocation definition
    looper.run(public_repo._sendSubmitReq(op))