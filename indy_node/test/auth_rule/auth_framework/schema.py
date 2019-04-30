import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import SCHEMA
from indy_node.test.api.helper import sdk_write_schema_and_check
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, AuthTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class SchemaTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.new_default_wallet = None

    def prepare(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Check default auth rule
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"], name='schema1',
                                   version='1.0')
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet, ["attrib1"], name='schema2',
                                       version='1.0')

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot send schema the old way
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"],
                                       name='schema3', version='1.0')

        # Step 4. Check, that new auth rule is used
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet, ["attrib1"], name='schema4',
                                   version='1.0')

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet, ["attrib1"], name='schema5',
                                   version='1.0')
        with pytest.raises(RequestRejectedException):
            sdk_write_schema_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet, ["attrib1"], name='schema6',
                                       version='1.0')

    def result(self):
        pass

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
