import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize import auth_map
from indy_common.constants import NYM, ROLE, ENDORSER
from indy_node.test.auth_rule.auth_framework.basic import roles_to_string, AuthTest
from indy_node.test.auth_rule.helper import create_verkey_did
from plenum.common.exceptions import RequestRejectedException

from indy_node.test.helper import build_auth_rule_request_json


class AddNewRoleTest(AuthTest):
    def __init__(self, action_id: str, creator_wallet, env):
        super().__init__(env, action_id)
        self.role = self.action.new_value
        self.role_string = roles_to_string[self.role]
        self.creator_wallet = creator_wallet
        self.checker_wallet = None

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

        # Step 3. Check, that we cannot add new nym with role by old way
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
        did, verkey = create_verkey_did(self.looper, wh)
        return self._build_nym(self.creator_wallet,
                               self.role_string,
                               did,
                               verkey=verkey,
                               skipverkey=False)

    def _get_nym_for_new_rule(self):
        wh, _ = self.checker_wallet
        did, verkey = create_verkey_did(self.looper, wh)
        return self._build_nym(self.checker_wallet,
                               self.role_string,
                               did,
                               verkey=verkey,
                               skipverkey=False)

    def get_changed_auth_rule(self):
        self.checker_wallet = self.env.role_to_wallet[ENDORSER]
        constraint = AuthConstraint(role=ENDORSER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.creator_wallet[1],
            auth_action=ADD_PREFIX,
            auth_type=NYM,
            field=ROLE,
            new_value=self.role,
            constraint=constraint.as_dict
        )


class AddNewTrusteeTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_trustee.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewStewardTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_steward.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewEndorserTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_endorser.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewNetworkMonitorTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_network_monitor.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)


class AddNewIdentityOwnerTest(AddNewRoleTest):
    def __init__(self, env, action_id=auth_map.add_new_identity_owner.get_action_id()):
        super().__init__(action_id, env.sdk_wallet_trustee, env)
