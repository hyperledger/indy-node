import pytest

from indy_node.test.pool_restart.helper import sdk_send_restart

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import POOL_RESTART
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, AuthTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests, sdk_sign_request_objects
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class RestartTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.test_nym = None

    def prepare(self):
        self.test_nym = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        for n in self.env.txnPoolNodeSet:
            n.actionReqHandler.restarter.handleRestartRequest = lambda *args, **kwargs: True

    def run(self):
        # Step 1. Check default auth rule
        sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot send txn the old way
        sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')

        # Step 4. Check, that we can send restart action in changed way
        sdk_send_restart(self.looper, self.new_default_wallet, self.sdk_pool_handle, action='start')

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = self.env.role_to_wallet[IDENTITY_OWNER]
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=POOL_RESTART,
                                                 field='action',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])
