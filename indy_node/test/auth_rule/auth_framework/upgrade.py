import pytest
from copy import deepcopy

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import POOL_UPGRADE, ACTION, CANCEL, JUSTIFICATION, SCHEDULE
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from indy_node.test.auth_rule.auth_framework.helper import send_and_check
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map


class UpgradeTest(AbstractTest):
    def __init__(self, env, action_id):
        self.looper = env.looper
        self.sdk_pool_handle = env.sdk_pool_handle
        self.trustee_wallet = env.sdk_wallet_trustee
        self.valid_upgrade = env.valid_upgrade

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.test_nym = None
        self.default_auth_rule_cancel = None
        self.changed_auth_rule_cancel = None

    def prepare(self):
        self.test_nym = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.default_auth_rule_cancel = self.get_default_auth_rule_cancel()
        self.changed_auth_rule_cancel = self.get_changed_auth_rule_cancel()

    def run(self):
        # Step 1. Check default auth rule
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)
        with pytest.raises(RequestRejectedException):
            sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.test_nym, self.valid_upgrade)

        # Canceling
        with pytest.raises(RequestRejectedException):
            self.cancel_upgrade(self.valid_upgrade, self.test_nym)
        self.cancel_upgrade(self.valid_upgrade, self.trustee_wallet)

        # Step 2. Change auth rule
        send_and_check(self, self.changed_auth_rule)
        send_and_check(self, self.changed_auth_rule_cancel)

        # Step 3. Check, that we cannot do txn the old way
        self.valid_upgrade['name'] += '1'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.test_nym, self.valid_upgrade)
        with pytest.raises(RequestRejectedException):
            sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)

        # Canceling
        with pytest.raises(RequestRejectedException):
            self.cancel_upgrade(self.valid_upgrade, self.trustee_wallet)
        self.cancel_upgrade(self.valid_upgrade, self.test_nym)

        # Step 4. Return default auth rule
        send_and_check(self, self.default_auth_rule)
        send_and_check(self, self.default_auth_rule_cancel)

        # Step 5. Check, that default auth rule works
        self.valid_upgrade['name'] += '2'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)
        with pytest.raises(RequestRejectedException):
            sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.test_nym, self.valid_upgrade)
        # Canceling
        with pytest.raises(RequestRejectedException):
            self.cancel_upgrade(self.valid_upgrade, self.test_nym)
        self.cancel_upgrade(self.valid_upgrade, self.trustee_wallet)

    def result(self):
        pass

    def get_nym(self, role):
        wh, _ = self.trustee_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.trustee_wallet, role, did)

    def get_default_auth_rule(self):
        action = AuthActionAdd(txn_type=POOL_UPGRADE,
                               field='action',
                               value='start')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=POOL_UPGRADE,
                                                 field='action',
                                                 new_value='start',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_default_auth_rule_cancel(self):
        action = AuthActionEdit(txn_type=POOL_UPGRADE,
                                field='action',
                                old_value='start',
                                new_value='cancel')
        constraint = auth_map.auth_map.get(action.get_action_id())
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=POOL_UPGRADE,
                                                 field='action',
                                                 old_value='start',
                                                 new_value='cancel',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=POOL_UPGRADE,
                                                 field='action',
                                                 new_value='start',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_changed_auth_rule_cancel(self):
        constraint = AuthConstraint(role=None,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=POOL_UPGRADE,
                                                 field='action',
                                                 old_value='start',
                                                 new_value='cancel',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def cancel_upgrade(self, upgrade, sdk_wallet):
        valid_upgrade_copy = deepcopy(upgrade)
        valid_upgrade_copy[ACTION] = CANCEL
        valid_upgrade_copy[JUSTIFICATION] = '"never gonna give you up"'

        valid_upgrade_copy.pop(SCHEDULE, None)
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, sdk_wallet, valid_upgrade_copy)
