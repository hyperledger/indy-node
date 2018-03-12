import pytest
import json
from indy_common.types import SafeRequest
from plenum.test.helper import sdk_send_and_check


def test_validate_get_revoc_reg_entry(build_get_revoc_reg_entry):
    req = build_get_revoc_reg_entry
    SafeRequest(**req)


@pytest.mark.skip("Not implemented")
def test_send_get_revoc_reg_entry(looper,
                                  txnPoolNodeSet,
                                  sdk_pool_handle,
                                  build_get_revoc_reg_entry):
    req = build_get_revoc_reg_entry
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)