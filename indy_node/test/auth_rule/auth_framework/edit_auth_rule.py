import pytest

from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import AUTH_RULE
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.auth_rule.helper import generate_auth_rule_operation, \
    sdk_send_and_check_auth_rule_request
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class AuthRuleTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

    def prepare(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Check default auth rule
        sdk_send_and_check_auth_rule_request(self.looper, self.trustee_wallet, self.sdk_pool_handle)
        with pytest.raises(RequestRejectedException):
            sdk_send_and_check_auth_rule_request(self.looper, self.new_default_wallet, self.sdk_pool_handle)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 3. Check, that we cannot send txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_send_and_check_auth_rule_request(self.looper, self.trustee_wallet, self.sdk_pool_handle)

        # Step 4. Check, that new auth rule is used
        sdk_send_and_check_auth_rule_request(self.looper, self.new_default_wallet, self.sdk_pool_handle)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.new_default_wallet)

        # Step 6. Check, that default auth rule works
        sdk_send_and_check_auth_rule_request(self.looper, self.trustee_wallet, self.sdk_pool_handle)
        with pytest.raises(RequestRejectedException):
            sdk_send_and_check_auth_rule_request(self.looper, self.new_default_wallet, self.sdk_pool_handle)

    def result(self):
        pass

    def get_default_auth_rule(self):
        action = AuthActionEdit(txn_type=AUTH_RULE,
                                field='*',
                                old_value='*',
                                new_value='*')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=AUTH_RULE,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.new_default_wallet[1])

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=AUTH_RULE,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])
