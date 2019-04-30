import json

import pytest

from indy_common.constants import TXN_ATHR_AGRMT_VERSION
from indy_node.test.taa_txn.helper import gen_random_txn_athr_agrmt
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.common.types import OPERATION
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


def test_send_valid_txn_athr_agrmt_succeeds(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    req = gen_random_txn_athr_agrmt(sdk_wallet_trustee[1])
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, json.dumps(req))
    sdk_get_and_check_replies(looper, [rep])


def test_send_invalid_txn_athr_agrmt_fails(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    req = gen_random_txn_athr_agrmt(sdk_wallet_trustee[1])
    req[OPERATION]['text'] = 42
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, json.dumps(req))
    with pytest.raises(RequestNackedException):
        sdk_get_and_check_replies(looper, [rep])


def test_send_valid_txn_athr_agrmt_without_enough_privileges_fails(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_steward):
    req = gen_random_txn_athr_agrmt(sdk_wallet_steward[1])
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_steward, sdk_pool_handle, json.dumps(req))
    with pytest.raises(RequestRejectedException):
        sdk_get_and_check_replies(looper, [rep])


def test_send_different_txn_athr_agrmt_with_same_version_fails(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    # Send original txn
    req = gen_random_txn_athr_agrmt(sdk_wallet_trustee[1])
    old_version = req[OPERATION][TXN_ATHR_AGRMT_VERSION]
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, json.dumps(req))
    sdk_get_and_check_replies(looper, [rep])

    # Send new txn with old version
    req = gen_random_txn_athr_agrmt(sdk_wallet_trustee[1])
    req[OPERATION][TXN_ATHR_AGRMT_VERSION] = old_version
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, json.dumps(req))
    with pytest.raises(RequestRejectedException):
        sdk_get_and_check_replies(looper, [rep])
