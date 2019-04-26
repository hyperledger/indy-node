import pytest
from indy_node.test.pool_restart.helper import sdk_send_restart

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import POOL_RESTART
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class RestartTest(AbstractTest):
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
        sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule)

        # Step 3. Check, that we cannot send txn the old way
        sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule)

        # Step 5. Check, that default auth rule works
        sdk_send_restart(self.looper, self.trustee_wallet, self.sdk_pool_handle, action='start')
        with pytest.raises(RequestRejectedException):
            sdk_send_restart(self.looper, self.test_nym, self.sdk_pool_handle, action='start')

    def result(self):
        pass

    def get_nym(self, role):
        wh, _ = self.trustee_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.trustee_wallet, role, did)

    def get_default_auth_rule(self):
        action = AuthActionAdd(txn_type=POOL_RESTART,
                               field='action',
                               value='*')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=POOL_RESTART,
                                                 field='action',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=POOL_RESTART,
                                                 field='action',
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
