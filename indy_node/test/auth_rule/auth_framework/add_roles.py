import pytest

from indy_common.authorize.auth_actions import AuthActionAdd, ADD_PREFIX, AbstractAuthAction, split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.authorize import auth_map
from indy_common.constants import NYM, ROLE, TRUST_ANCHOR, NETWORK_MONITOR
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, roles_to_string, AuthTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_multi_sign_request_objects, sdk_send_signed_requests, sdk_get_and_check_replies, \
    sdk_gen_request, sdk_sign_request_objects


class AddNewRoleTest(AuthTest):
    def __init__(self, action_id: str, creator_wallet, env):
        self.action_id = action_id
        self.action = split_action_id(action_id)
        self.role = self.action.new_value
        self.role_string = roles_to_string[self.role]
        self.creator_wallet = creator_wallet
        self.trustee_wallet = env.sdk_wallet_trustee
        self.looper = env.looper
        self.sdk_pool_handle = env.sdk_pool_handle
        self.checker_wallet = None
        self.env = env

    def prepare(self):
        self.phase_req_1 = self.get_nym()
        self.phase_req_2 = self.get_nym()
        self.phase_req_3 = self.get_nym()

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.nym_for_new_rule = self._get_nym_for_new_rule()

    def run(self):
        # Step 1. Check default auth rule
        self.send_and_check(self.phase_req_1, wallet=self.creator_wallet)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot add new steward by old way
        with pytest.raises(RequestRejectedException):
            self.send_and_check(self.phase_req_2, wallet=self.creator_wallet)

        # Step 4. Check, that new rule is working
        self.send_and_check(self.nym_for_new_rule, wallet=self.checker_wallet)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        self.send_and_check(self.phase_req_3, wallet=self.creator_wallet)

    def result(self):
        pass

    def get_nym(self):
        wh, _ = self.creator_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.creator_wallet, self.role_string, did)

    def _get_nym_for_new_rule(self):
        wh, _ = self.checker_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.checker_wallet,
                               self.role_string,
                               did)

    def get_changed_auth_rule(self):
        self.checker_wallet = self.env.role_to_wallet[TRUST_ANCHOR]
        constraint = AuthConstraint(role=TRUST_ANCHOR,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=NYM,
                                                 field=ROLE,
                                                 new_value=self.role,
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.creator_wallet[1])


class AddNewTrusteeTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_trustee.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewStewardTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_steward.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewTrustAnchorTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_trust_anchor.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewNetworkMonitorTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_network_monitor.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewIdentityOwnerTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_identity_owner.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)
