import pytest

from indy_node.test.pool_config.helper import sdk_ensure_pool_config_sent

from indy_common.authorize.auth_actions import EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import POOL_CONFIG
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from plenum.common.exceptions import RequestRejectedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.helper import build_auth_rule_request_json


class PoolConfigTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.pool_config_wtff = env.pool_config_wtff

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Check default auth rule
        sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.pool_config_wtff)
        with pytest.raises(RequestRejectedException):
            sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.new_default_wallet, self.pool_config_wtff)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 3. Check, that we cannot send txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.pool_config_wtff)

        # Step 4. Check, that new auth rule is used
        sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.new_default_wallet, self.pool_config_wtff)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.pool_config_wtff)
        with pytest.raises(RequestRejectedException):
            sdk_ensure_pool_config_sent(self.looper, self.sdk_pool_handle, self.new_default_wallet, self.pool_config_wtff)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=EDIT_PREFIX,
            auth_type=POOL_CONFIG,
            field='action',
            old_value='*',
            new_value='*',
            constraint=constraint.as_dict
        )
