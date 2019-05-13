import json

import pytest

from indy_common.authorize.auth_map import steward_or_trustee_constraint
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.test.auth_rule.helper import sdk_send_and_check_auth_rule_request
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_VERSION, TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.txn_author_agreement.helper import get_config_req_handler, sdk_send_txn_author_agreement


def test_send_valid_txn_author_agreement_succeeds(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee):
    text = randomString(1024)
    version = randomString(16)
    sdk_send_txn_author_agreement(looper, sdk_pool_handle, sdk_wallet_trustee, text, version)

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
