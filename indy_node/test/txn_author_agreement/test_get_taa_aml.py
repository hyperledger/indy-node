import json
from random import randint

import pytest
from plenum.common.exceptions import RequestNackedException
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request

from plenum.common.util import randomString
from plenum.common.constants import TXN_TYPE, GET_TXN_AUTHOR_AGREEMENT_AML, CURRENT_PROTOCOL_VERSION
from plenum.common.types import OPERATION, f


def test_get_taa_aml_static_validation_fails(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_client):
    req = {
        OPERATION: {
            TXN_TYPE: GET_TXN_AUTHOR_AGREEMENT_AML,
            'timestamp': randint(1, 2147483647),
            'version': randomString()
        },
        f.IDENTIFIER.nm: sdk_wallet_client[1],
        f.REQ_ID.nm: randint(1, 2147483647),
        f.PROTOCOL_VERSION.nm: CURRENT_PROTOCOL_VERSION
    }
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_client, sdk_pool_handle, json.dumps(req))
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [rep])
    e.match('cannot be used in GET_TXN_AUTHOR_AGREEMENT_AML request together')
