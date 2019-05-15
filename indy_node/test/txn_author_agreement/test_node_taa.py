import pytest

from indy_common.authorize.auth_map import steward_or_trustee_constraint
from indy_node.test.auth_rule.helper import sdk_send_and_check_auth_rule_request
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_TEXT, \
    TXN_AUTHOR_AGREEMENT, REPLY
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.txn_author_agreement.helper import sdk_send_txn_author_agreement, sdk_get_txn_author_agreement


def test_send_valid_txn_author_agreement_succeeds(looper, txnPoolNodeSet, sdk_pool_handle,
                                                  sdk_wallet_trustee, sdk_wallet_client):
    text = randomString(1024)
    version = randomString(16)
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, text, version)

    reply = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_client)[1]
    assert reply['op'] == REPLY

    result = reply['result']['data']
    assert result[TXN_AUTHOR_AGREEMENT_TEXT] == text
    assert result[TXN_AUTHOR_AGREEMENT_VERSION] == version


def test_send_valid_txn_author_agreement_without_enough_privileges_fails(looper, txnPoolNodeSet, sdk_pool_handle,
                                                                         sdk_wallet_steward):
    with pytest.raises(RequestRejectedException):
        sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_steward,
                                      randomString(1024), randomString(16))


def test_txn_author_agreement_respects_current_auth_rules(looper, txnPoolNodeSet, sdk_pool_handle,
                                                          sdk_wallet_trustee, sdk_wallet_steward):
    sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_type=TXN_AUTHOR_AGREEMENT, field='*', new_value='*',
                                         constraint=steward_or_trustee_constraint.as_dict)

    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_steward,
                                  randomString(1024), randomString(16))
