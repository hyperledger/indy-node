import json

import pytest
from plenum.common.constants import TRUSTEE

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import ATTRIB
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from indy_node.test.helper import (
    sdk_add_attribute_and_check, build_auth_rule_request_json
)
from plenum.common.exceptions import RequestRejectedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym


class AddAttribTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.attr_data = None

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

        self.attr_data = {'name': 'Albus'}

    def run(self):
        # Step 1. Check default auth rule
        self.new_default_wallet = self.new_client_wallet()
        sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet,
                                    json.dumps(self.attr_data), self.new_default_wallet[1])
        with pytest.raises(RequestRejectedException):
            self.new_default_wallet = self.new_client_wallet()
            sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                                        json.dumps(self.attr_data), self.new_default_wallet[1])

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot send attrib the old way
        with pytest.raises(RequestRejectedException):
            self.new_default_wallet = self.new_client_wallet()
            sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet,
                                        json.dumps(self.attr_data), self.new_default_wallet[1])

        # Step 4. Check, that new auth rule is used
        self.new_default_wallet = self.new_client_wallet()
        sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                                    json.dumps(self.attr_data), self.new_default_wallet[1])

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        self.new_default_wallet = self.new_client_wallet()
        sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.new_default_wallet,
                                    json.dumps(self.attr_data), self.new_default_wallet[1])
        with pytest.raises(RequestRejectedException):
            self.new_default_wallet = self.new_client_wallet()
            sdk_add_attribute_and_check(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                                        json.dumps(self.attr_data), self.new_default_wallet[1])

    def result(self):
        pass

    def get_changed_auth_rule(self):
        sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                        role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=TRUSTEE,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=ADD_PREFIX,
            auth_type=ATTRIB,
            field='*',
            new_value='*',
            constraint=constraint.as_dict
        )

    def new_client_wallet(self):
        return sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                               role=IDENTITY_OWNER)
