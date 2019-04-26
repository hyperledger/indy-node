import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import SCHEMA
from indy_node.test.api.helper import sdk_write_schema_and_check
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from indy_node.test.auth_rule.auth_framework.helper import send_and_check
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class SchemaTest(AbstractTest):
    def __init__(self, env, action_id):
        self.looper = env.looper
        self.sdk_pool_handle = env.sdk_pool_handle
        self.trustee_wallet = env.sdk_wallet_trustee

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.test_nym = None

    def prepare(self):
        self.test_nym = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Check default auth rule
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"], name='schema1',
                                   version='1.0')
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.test_nym, ["attrib1"], name='schema2',
                                       version='1.0')

        # Step 2. Change auth rule
        send_and_check(self, self.changed_auth_rule)

        # Step 3. Check, that we cannot send schema the old way
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"],
                                       name='schema3', version='1.0')
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.test_nym, ["attrib1"], name='schema4',
                                   version='1.0')

        # Step 4. Return default auth rule
        send_and_check(self, self.default_auth_rule)

        # Step 5. Check, that default auth rule works
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"], name='schema5',
                                   version='1.0')
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.test_nym, ["attrib1"], name='schema6',
                                       version='1.0')

    def result(self):
        pass

    def get_nym(self, role):
        wh, _ = self.trustee_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.trustee_wallet, role, did)

    def get_default_auth_rule(self):
        action = AuthActionAdd(SCHEMA, '*', value='*')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=SCHEMA,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=SCHEMA,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])
