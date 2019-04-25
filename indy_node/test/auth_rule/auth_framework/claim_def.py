import json

import pytest
from indy.ledger import build_get_schema_request, parse_get_schema_response

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import CLAIM_DEF
from indy_node.test.api.helper import sdk_write_schema
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from indy_node.test.claim_def.test_send_claim_def import sdk_send_claim_def
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests, sdk_sign_and_submit_req, sdk_get_reply
from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_sign_and_send_prepared_request
from indy_common.authorize import auth_map


def get_schema_json(looper, sdk_pool_handle, sdk_wallet_trustee):
    wallet_handle, identifier = sdk_wallet_trustee
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))
    return schema_json


class ClaimDefTest(AbstractTest):
    def __init__(self, env):
        self.looper = env.looper
        self.sdk_pool_handle = env.sdk_pool_handle
        self.trustee_wallet = env.sdk_wallet_trustee

        self.default_auth_rule = None
        self.changed_auth_rule = None

        self.default_auth_rule_edit = None
        self.changed_auth_rule_edit = None
        self.test_nym = None

    def prepare(self):
        self.test_nym = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.default_auth_rule_edit = self.get_default_auth_rule_edit()
        self.changed_auth_rule_edit = self.get_changed_auth_rule_edit()

    def run(self):
        schema_json = get_schema_json(self.looper, self.sdk_pool_handle, self.trustee_wallet)
        # Step 1. Check default auth rule
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag1', schema_json)
        with pytest.raises(RequestRejectedException):
            sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.test_nym, 'tag2', schema_json)

        # Edit
        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))
        sdk_get_and_check_replies(self.looper, [req_couple])

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule)
        self.send_and_check(self.changed_auth_rule_edit)

        # Step 3. Check, that we cannot send schema the old way
        with pytest.raises(RequestRejectedException):
            sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag3', schema_json)
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.test_nym, 'tag4', schema_json)

        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.test_nym, self.sdk_pool_handle,
                                                        json.dumps(req))
        with pytest.raises(RequestRejectedException) as e:
            sdk_get_and_check_replies(self.looper, [req_couple])
        e.match('Not enough TRUSTEE signatures')

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule)
        self.send_and_check(self.default_auth_rule_edit)

        # Step 5. Check, that default auth rule works
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag5', schema_json)
        with pytest.raises(RequestRejectedException):
            sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.test_nym, 'tag6', schema_json)

        # Edit
        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))
        sdk_get_and_check_replies(self.looper, [req_couple])

    def result(self):
        pass

    def get_nym(self, role):
        wh, _ = self.trustee_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.trustee_wallet, role, did)

    def get_default_auth_rule(self):
        action = AuthActionAdd(CLAIM_DEF, '*', value='*')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_default_auth_rule_edit(self):
        action = AuthActionEdit(CLAIM_DEF, field='*', old_value='*', new_value='*')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule_edit(self):
        constraint = AuthConstraint(role=TRUSTEE,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def send_and_check(self, req):
        signed_reqs = sdk_multi_sign_request_objects(self.looper,
                                                     [self.trustee_wallet],
                                                     [req])
        request_couple = sdk_send_signed_requests(self.sdk_pool_handle,
                                                  signed_reqs)[0]

        return sdk_get_and_check_replies(self.looper, [request_couple])[0]
