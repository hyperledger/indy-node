import json

import pytest
from indy.did import create_and_store_my_did
from indy.ledger import build_nym_request

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import SCHEMA, ROLE, NYM
from indy_node.test.api.helper import sdk_write_schema_and_check, sdk_build_schema_request
from indy_node.test.endorser.helper import sdk_submit_and_check_by_endorser, sdk_append_request_endorser
from indy_node.test.helper import build_auth_rule_request_json, sdk_send_and_check_req_json
from indy_node.test.nym_txn.test_create_did_without_endorser import NEW_ROLE
from plenum.common.constants import TRUSTEE, VERKEY

from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.common.util import randomString
from plenum.server.request_handlers.utils import get_nym_details
from plenum.test.helper import sdk_multisign_request_object, sdk_get_and_check_replies, sdk_send_signed_requests


def test_send_by_endorser(looper, sdk_pool_handle, sdk_wallet_new_client, sdk_wallet_endorser):
    # try writing without Endorser by a None-role client
    with pytest.raises(RequestRejectedException):
        sdk_write_schema_and_check(looper, sdk_pool_handle, sdk_wallet_new_client,
                                   ["attr1", "attr2"], "name1", "1.0")

    # write with Endorser
    req_json = sdk_build_schema_request(looper, sdk_wallet_new_client,
                                        ["attr1", "attr2"], "name1", "1.0")
    sdk_submit_and_check_by_endorser(looper, sdk_pool_handle,
                                     sdk_wallet_author=sdk_wallet_new_client, sdk_wallet_endorser=sdk_wallet_endorser,
                                     request_json=req_json)


def test_both_author_and_endorser_must_sign(looper, sdk_pool_handle, sdk_wallet_trustee, sdk_wallet_endorser):
    '''
    Both author and endorser must sign the request even if the author can send the request without Endorser
    '''
    req_json = sdk_build_schema_request(looper, sdk_wallet_trustee,
                                        ["attr1", "attr2"], "name1", "2.0")
    req_json = sdk_append_request_endorser(looper, req_json, sdk_wallet_endorser[1])

    # sign by Author only
    req_json_author_only = sdk_multisign_request_object(looper, sdk_wallet_trustee, req_json)
    with pytest.raises(RequestNackedException, match="Endorser must sign the request"):
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_author_only])[0]
        sdk_get_and_check_replies(looper, [request_couple])

    # sign by Endorser only
    req_json_endorser_only = sdk_multisign_request_object(looper, sdk_wallet_endorser, req_json)
    with pytest.raises(RequestNackedException, match="Author must sign the request when sending via Endorser"):
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_endorser_only])[0]
        sdk_get_and_check_replies(looper, [request_couple])

    # sign by both
    req_json_both = sdk_multisign_request_object(looper, sdk_wallet_trustee, req_json)
    req_json_both = sdk_multisign_request_object(looper, sdk_wallet_endorser, req_json_both)
    request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json_both])[0]
    sdk_get_and_check_replies(looper, [request_couple])


def test_endorser_field_must_be_explicit(looper, sdk_pool_handle, sdk_wallet_new_client, sdk_wallet_endorser):
    req_json = sdk_build_schema_request(looper, sdk_wallet_new_client,
                                        ["attr1", "attr2"], "name2", "3.0")
    # Do not append Endorser field!

    # sign by both Author and Endorser
    req_json = sdk_multisign_request_object(looper, sdk_wallet_new_client, req_json)
    req_json = sdk_multisign_request_object(looper, sdk_wallet_endorser, req_json)

    with pytest.raises(RequestRejectedException,
                       match="'Endorser' field must be explicitly set for the endorsed transaction"):
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json])[0]
        sdk_get_and_check_replies(looper, [request_couple])


def test_endorser_must_have_known_role(looper, sdk_pool_handle, sdk_wallet_new_client, sdk_wallet_trustee):
    req_json = sdk_build_schema_request(looper, sdk_wallet_trustee,
                                        ["attr1", "attr2"], "name3", "4.0")
    with pytest.raises(RequestRejectedException, match="Endorser must have one of the following roles"):
        sdk_submit_and_check_by_endorser(looper, sdk_pool_handle,
                                         sdk_wallet_author=sdk_wallet_trustee,
                                         sdk_wallet_endorser=sdk_wallet_new_client,
                                         request_json=req_json)


def test_endorser_not_required_when_two_trustee_sigs(looper, sdk_pool_handle, sdk_wallet_trustee_list):
    change_new_schema_auth_rule(looper, sdk_pool_handle, sdk_wallet_trustee_list[0],
                                constraint=AuthConstraint(role=TRUSTEE, sig_count=2))

    req_json = sdk_build_schema_request(looper, sdk_wallet_trustee_list[1],
                                        ["attr1", "attr2"], "name4", "5.0")
    # sign by both
    req_json = sdk_multisign_request_object(looper, sdk_wallet_trustee_list[1], req_json)
    req_json = sdk_multisign_request_object(looper, sdk_wallet_trustee_list[2], req_json)
    request_couple = sdk_send_signed_requests(sdk_pool_handle, [req_json])[0]
    sdk_get_and_check_replies(looper, [request_couple])


def test_endorser_required_when_multi_sig_with_off_ledger_signature(looper, txnPoolNodeSet,
                                                                    sdk_wallet_client,
                                                                    sdk_pool_handle,
                                                                    sdk_wallet_trustee,
                                                                    sdk_wallet_endorser):
    change_new_did_auth_rule(looper, sdk_pool_handle, sdk_wallet_trustee,
                             constraint=AuthConstraint(role='*',
                                                       sig_count=2,
                                                       off_ledger_signature=True))

    new_did, verkey = \
        looper.loop.run_until_complete(
            create_and_store_my_did(sdk_wallet_client[0], json.dumps({'seed': randomString(32)})))
    sdk_wallet_new_client = (sdk_wallet_client[0], new_did)
    nym_request = looper.loop.run_until_complete(
        build_nym_request(new_did, new_did, verkey, None, IDENTITY_OWNER))

    # can not send without Endorser
    with pytest.raises(RequestRejectedException,
                       match="'Endorser' field must be explicitly set for the endorsed transaction"):
        signed_req = sdk_multisign_request_object(looper, sdk_wallet_new_client, nym_request)
        signed_req = sdk_multisign_request_object(looper, sdk_wallet_endorser, signed_req)
        request_couple = sdk_send_signed_requests(sdk_pool_handle, [signed_req])[0]
        sdk_get_and_check_replies(looper, [request_couple])

    # can send with Endorser
    sdk_submit_and_check_by_endorser(looper, sdk_pool_handle,
                                     sdk_wallet_author=sdk_wallet_new_client, sdk_wallet_endorser=sdk_wallet_endorser,
                                     request_json=nym_request)
    details = get_nym_details(txnPoolNodeSet[0].states[1], new_did, is_committed=True)
    assert details[ROLE] == IDENTITY_OWNER
    assert details[VERKEY] == verkey


def change_new_schema_auth_rule(looper, sdk_pool_handle, sdk_wallet_trustee, constraint):
    req = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1],
        auth_action=ADD_PREFIX,
        auth_type=SCHEMA,
        field='*',
        old_value=None,
        new_value='*',
        constraint=constraint.as_dict
    )

    sdk_send_and_check_req_json(looper, sdk_pool_handle, sdk_wallet_trustee, req)


def change_new_did_auth_rule(looper, sdk_pool_handle, sdk_wallet_trustee, constraint):
    req = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1],
        auth_action=ADD_PREFIX,
        auth_type=NYM,
        field=ROLE,
        old_value=None,
        new_value=NEW_ROLE,
        constraint=constraint.as_dict
    )

    sdk_send_and_check_req_json(looper, sdk_pool_handle, sdk_wallet_trustee, req)
