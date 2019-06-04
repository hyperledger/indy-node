import json

import pytest
from indy.ledger import build_acceptance_mechanisms_request

from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_map import steward_or_trustee_constraint
from indy_node.test.helper import sdk_send_and_check_auth_rule_request
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_TEXT, \
    TXN_AUTHOR_AGREEMENT, REPLY
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.txn_author_agreement.helper import sdk_send_txn_author_agreement, sdk_get_txn_author_agreement


@pytest.fixture(scope="module")
def taa_aml_request_module(looper, sdk_pool_handle, sdk_wallet_trustee):
    return looper.loop.run_until_complete(build_acceptance_mechanisms_request(
        sdk_wallet_trustee[1],
        json.dumps({
            'Nice way': 'very good way to accept agreement'}),
        randomString(), randomString()))


@pytest.fixture(scope="module")
def setup_aml(looper, txnPoolNodeSet, taa_aml_request_module, sdk_pool_handle, sdk_wallet_trustee):
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, taa_aml_request_module)
    sdk_get_and_check_replies(looper, [req])


def test_send_valid_txn_author_agreement_succeeds(looper, setup_aml, txnPoolNodeSet, sdk_pool_handle,
                                                  sdk_wallet_trustee, sdk_wallet_client):
    text = randomString(1024)
    version = randomString(16)
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, text, version)

    reply = sdk_get_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_client)[1]
    assert reply['op'] == REPLY

    result = reply['result']['data']
    assert result[TXN_AUTHOR_AGREEMENT_TEXT] == text
    assert result[TXN_AUTHOR_AGREEMENT_VERSION] == version


def test_send_valid_txn_author_agreement_without_enough_privileges_fails(looper, setup_aml, txnPoolNodeSet,
                                                                         sdk_pool_handle,
                                                                         sdk_wallet_steward):
    with pytest.raises(RequestRejectedException):
        sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_steward,
                                      randomString(1024), randomString(16))


def test_txn_author_agreement_respects_current_auth_rules(looper, setup_aml, txnPoolNodeSet, sdk_pool_handle,
                                                          sdk_wallet_trustee, sdk_wallet_steward):
    sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX, auth_type=TXN_AUTHOR_AGREEMENT,
                                         field='*', new_value='*',
                                         constraint=steward_or_trustee_constraint.as_dict)

    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_steward,
                                  randomString(1024), randomString(16))
