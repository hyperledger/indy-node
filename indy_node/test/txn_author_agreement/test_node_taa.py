import json

import pytest

from indy_common.authorize.auth_map import steward_or_trustee_constraint
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.test.auth_rule.helper import sdk_send_and_check_auth_rule_request
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT
from plenum.common.exceptions import RequestRejectedException
from plenum.common.types import OPERATION
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request
from plenum.test.txn_author_agreement.helper import prepare_txn_author_agreement, get_config_req_handler


def test_send_valid_txn_author_agreement_succeeds(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    req = looper.loop.run_until_complete(prepare_txn_author_agreement(sdk_wallet_trustee[1]))
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee, sdk_pool_handle, req)
    sdk_get_and_check_replies(looper, [rep])

    req = json.loads(req)
    version = req[OPERATION][TXN_AUTHOR_AGREEMENT_VERSION]
    text = req[OPERATION][TXN_AUTHOR_AGREEMENT_TEXT]
    digest = ConfigReqHandler._taa_digest(version, text)

    # TODO: Replace this with get transaction
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)
    for node in txnPoolNodeSet:
        config_req_handler = get_config_req_handler(node)
        assert config_req_handler.get_taa_digest() == digest.encode()
        assert config_req_handler.get_taa_digest(version) == digest.encode()

        taa = config_req_handler.state.get(ConfigReqHandler._state_path_taa_digest(digest))
        assert taa is not None

        taa = json.loads(taa.decode())
        assert taa[TXN_AUTHOR_AGREEMENT_VERSION] == version
        assert taa[TXN_AUTHOR_AGREEMENT_TEXT] == text


def test_send_valid_txn_author_agreement_without_enough_privileges_fails(looper, txnPoolNodeSet, sdk_pool_handle,
                                                                         sdk_wallet_steward):
    req = looper.loop.run_until_complete(prepare_txn_author_agreement(sdk_wallet_steward[1]))
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_steward, sdk_pool_handle, req)

    with pytest.raises(RequestRejectedException):
        sdk_get_and_check_replies(looper, [rep])


def test_txn_author_agreement_respects_current_auth_rules(looper, txnPoolNodeSet, sdk_pool_handle,
                                                          sdk_wallet_trustee, sdk_wallet_steward):
    sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_type=TXN_AUTHOR_AGREEMENT, field='*', new_value='*',
                                         constraint=steward_or_trustee_constraint.as_dict)

    req = looper.loop.run_until_complete(prepare_txn_author_agreement(sdk_wallet_steward[1]))
    rep = sdk_sign_and_send_prepared_request(looper, sdk_wallet_steward, sdk_pool_handle, req)
    sdk_get_and_check_replies(looper, [rep])
