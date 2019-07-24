import json

import pytest
from indy.did import create_and_store_my_did
from indy.ledger import build_nym_request

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, NEED_TO_BE_ON_LEDGER
from indy_common.constants import CONSTRAINT
from indy_node.test.helper import build_auth_rule_request_json, sdk_send_and_check_req_json
from plenum.common.constants import ROLE, VERKEY, NYM
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from plenum.common.types import OPERATION
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import get_nym_details
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request

NEW_ROLE = None


# Note: Similar tests written in plenum, because of specific of signature
# validation, which requires to duplicate verification code

@pytest.fixture(scope='function')
def nym_txn_data(looper, sdk_wallet_client):
    seed = randomString(32)

    wh, _ = sdk_wallet_client
    sender_did, sender_verkey = \
        looper.loop.run_until_complete(create_and_store_my_did(wh, json.dumps({'seed': seed})))
    return wh, randomString(5), sender_did, sender_verkey


@pytest.fixture(scope='module')
def changed_auth_rule(looper, sdk_pool_handle, sdk_wallet_trustee):
    constraint = AuthConstraint(role='*',
                                sig_count=1,
                                need_to_be_on_ledger=False)
    req = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1],
        auth_action=ADD_PREFIX,
        auth_type=NYM,
        field=ROLE,
        old_value=None,
        new_value=NEW_ROLE,
        constraint=constraint.as_dict
    )
    req = json.loads(req)
    req[OPERATION][CONSTRAINT][NEED_TO_BE_ON_LEDGER] = False
    req = json.dumps(req)

    sdk_send_and_check_req_json(looper, sdk_pool_handle, sdk_wallet_trustee, req)


def test_create_did_without_endorser_fails(looper, txnPoolNodeSet, nym_txn_data, sdk_pool_handle):
    wh, alias, sender_did, sender_verkey = nym_txn_data
    nym_request = looper.loop.run_until_complete(
        build_nym_request(sender_did, sender_did, sender_verkey, alias, NEW_ROLE))

    request_couple = sdk_sign_and_send_prepared_request(looper, (wh, sender_did), sdk_pool_handle, nym_request)
    with pytest.raises(RequestRejectedException, match='is not found in the Ledger'):
        sdk_get_and_check_replies(looper, [request_couple])


def test_create_did_without_endorser(looper, txnPoolNodeSet, nym_txn_data, sdk_pool_handle, changed_auth_rule):
    wh, alias, sender_did, sender_verkey = nym_txn_data
    nym_request = looper.loop.run_until_complete(
        build_nym_request(sender_did, sender_did, sender_verkey, alias, NEW_ROLE))

    request_couple = sdk_sign_and_send_prepared_request(looper, (wh, sender_did), sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [request_couple])

    details = get_nym_details(txnPoolNodeSet[0].states[1], sender_did, is_committed=True)
    assert details[ROLE] == NEW_ROLE
    assert details[VERKEY] == sender_verkey


def test_create_did_without_endorser_empty_verkey(looper, nym_txn_data, sdk_wallet_client, sdk_pool_handle):
    wh, alias, sender_did, sender_verkey = nym_txn_data

    nym_request = looper.loop.run_until_complete(build_nym_request(sender_did, sender_did, None, alias, NEW_ROLE))

    request_couple = sdk_sign_and_send_prepared_request(looper, (wh, sender_did), sdk_pool_handle, nym_request)

    with pytest.raises(RequestNackedException, match='Can not find verkey for {}'.format(sender_did)):
        sdk_get_and_check_replies(looper, [request_couple])


def test_create_did_without_endorser_with_different_dest(looper, nym_txn_data, sdk_wallet_client, sdk_pool_handle):
    wh, alias, sender_did, sender_verkey = nym_txn_data

    nym_request = looper.loop.run_until_complete(
        build_nym_request(sender_did, sdk_wallet_client[1], sender_verkey, alias, NEW_ROLE))

    request_couple = sdk_sign_and_send_prepared_request(looper, (wh, sender_did), sdk_pool_handle, nym_request)

    with pytest.raises(RequestNackedException, match='Can not find verkey for {}'.format(sender_did)):
        sdk_get_and_check_replies(looper, [request_couple])
