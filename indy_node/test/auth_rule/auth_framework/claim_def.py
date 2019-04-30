import json

import pytest
from indy.ledger import build_get_schema_request, parse_get_schema_response

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, AuthActionEdit, EDIT_PREFIX, split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import CLAIM_DEF
from indy_node.test.api.helper import sdk_write_schema
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, AuthTest
from indy_node.test.auth_rule.auth_framework.helper import send_and_check
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


class AddClaimDefTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

        self.default_auth_rule = None
        self.changed_auth_rule = None

        self.default_auth_rule_edit = None
        self.changed_auth_rule_edit = None
        self.new_default_edit_wallet = None
        self.new_default_add_wallet = None
        self.new_default_wallet = None

    def prepare(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        schema_json = get_schema_json(self.looper, self.sdk_pool_handle, self.trustee_wallet)

        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag1', schema_json)

        # Step 3. Check, that new auth rule is used
        sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.new_default_wallet, 'tag2', schema_json)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag3', schema_json)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_add_wallet = self.env.role_to_wallet[IDENTITY_OWNER]
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])


class EditClaimDefTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

        self.default_auth_rule = None
        self.changed_auth_rule = None

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.new_default_edit = None
        self.new_default_wallet = None

    def prepare(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        schema_json = get_schema_json(self.looper, self.sdk_pool_handle, self.trustee_wallet)
        # Step 1. Check default auth rule
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag1', schema_json)
        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))
        sdk_get_and_check_replies(self.looper, [req_couple])

        # Step 2. Change auth rule
        send_and_check(self, self.changed_auth_rule)

        # Step 3. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag2', schema_json)
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.new_default_wallet, 'tag3', schema_json)

        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.new_default_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))
        with pytest.raises(RequestRejectedException) as e:
            sdk_get_and_check_replies(self.looper, [req_couple])
        e.match('Not enough TRUSTEE signatures')

        # Step 4, Check, that new auth rule is used
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.new_default_wallet, 'tag4', schema_json)

        req = reply[0][0]['operation']
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.new_default_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))

        sdk_get_and_check_replies(self.looper, [req_couple])

        # Step 5. Return default auth rule
        send_and_check(self, self.default_auth_rule)

        # Step 6. Check, that default auth rule works
        reply = sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag5', schema_json)
        req = reply[0][0]
        req['operation']['data']['primary']['n'] = 'abc'
        req_couple = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                        json.dumps(req))
        sdk_get_and_check_replies(self.looper, [req_couple])

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = self.env.role_to_wallet[IDENTITY_OWNER]
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=CLAIM_DEF,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])
