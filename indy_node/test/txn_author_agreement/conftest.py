import json

import pytest
from indy.ledger import build_acceptance_mechanisms_request

from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


@pytest.fixture(scope="module")
def setup_aml(looper, txnPoolNodeSet, taa_aml_request_module, sdk_pool_handle, sdk_wallet_trustee):
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, taa_aml_request_module)
    sdk_get_and_check_replies(looper, [req])


@pytest.fixture(scope="module")
def taa_aml_request_module(looper, sdk_pool_handle, sdk_wallet_trustee):
    return looper.loop.run_until_complete(build_acceptance_mechanisms_request(
        sdk_wallet_trustee[1],
        json.dumps({
            'Nice way': 'very good way to accept agreement'}),
        randomString(), randomString()))
