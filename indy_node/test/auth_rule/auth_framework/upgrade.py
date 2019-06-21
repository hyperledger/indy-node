import pytest
from copy import deepcopy

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import POOL_UPGRADE, ACTION, CANCEL, JUSTIFICATION, SCHEDULE, CONFIG_LEDGER_ID
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent
from plenum.common.exceptions import RequestRejectedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_common.authorize import auth_map

from indy_node.test.helper import build_auth_rule_request_json


class StartUpgradeTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.valid_upgrade = env.valid_upgrade

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        for n in self.env.txnPoolNodeSet:
            n.upgrader.handleUpgradeTxn = lambda *args, **kwargs: True

    def run(self):

        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that new auth rule is used
        self.valid_upgrade['name'] += '1'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.new_default_wallet, self.valid_upgrade)

        # Step 3. Check that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.valid_upgrade['name'] += '2'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=ADD_PREFIX,
            auth_type=POOL_UPGRADE,
            field='action',
            new_value='start',
            constraint=constraint.as_dict
        )


class CancelUpgradeTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.valid_upgrade = env.valid_upgrade

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        for n in self.env.txnPoolNodeSet:
            n.upgrader.handleUpgradeTxn = lambda *args, **kwargs: True

    def run(self):

        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check that we cannot do txn the old way
        self.valid_upgrade['name'] += '1'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)

        with pytest.raises(RequestRejectedException):
            self.cancel_upgrade(self.valid_upgrade, self.trustee_wallet)

        # Step 3. Check, that new auth rule is used
        self.cancel_upgrade(self.valid_upgrade, self.new_default_wallet)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        self.valid_upgrade['name'] += '2'
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, self.trustee_wallet, self.valid_upgrade)
        self.cancel_upgrade(self.valid_upgrade, self.trustee_wallet)

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
            auth_type=POOL_UPGRADE,
            field='action',
            old_value='start',
            new_value='cancel',
            constraint=constraint.as_dict
        )

    def cancel_upgrade(self, upgrade, sdk_wallet):
        valid_upgrade_copy = deepcopy(upgrade)
        valid_upgrade_copy[ACTION] = CANCEL
        valid_upgrade_copy[JUSTIFICATION] = '"never gonna give you up"'

        valid_upgrade_copy.pop(SCHEDULE, None)
        sdk_ensure_upgrade_sent(self.looper, self.sdk_pool_handle, sdk_wallet, valid_upgrade_copy)
