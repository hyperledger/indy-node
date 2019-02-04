import pytest
import json

from indy_node.test.validator_info.helper import sdk_get_validator_info
from plenum.common.exceptions import RequestRejectedException

from indy_common.constants import VALIDATOR_INFO
from plenum.common.constants import REPLY, TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply, sdk_send_signed_requests, sdk_get_and_check_replies


def test_validator_info_command(
        sdk_pool_handle, sdk_wallet_trustee, looper):
    req, resp = sdk_get_validator_info(looper,
                                 sdk_wallet_trustee,
                               sdk_pool_handle)
    _comparison_reply(resp, req)


def test_fail_validator_info_command(
        sdk_pool_handle, sdk_wallet_client, looper):
    with pytest.raises(RequestRejectedException) as excinfo:
        sdk_get_validator_info(looper,
                               sdk_wallet_client,
                               sdk_pool_handle)
    assert excinfo.match("Rule for this action is")


def _comparison_reply(responses, req_obj):
    for json_resp in responses.values():
        resp = json.loads(json_resp)
        assert resp["op"] == REPLY
        assert resp[f.RESULT.nm][f.IDENTIFIER.nm] == req_obj[f.IDENTIFIER.nm]
        assert resp[f.RESULT.nm][f.REQ_ID.nm] == req_obj[f.REQ_ID.nm]
        assert resp[f.RESULT.nm][TXN_TYPE] == VALIDATOR_INFO
        assert resp[f.RESULT.nm][DATA] is not None


