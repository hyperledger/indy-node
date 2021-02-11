import pytest
from plenum.common.constants import STEWARD, TRUSTEE_STRING, LEDGERS_FREEZE

from indy_node.server.request_handlers.action_req_handlers.pool_restart_handler import PoolRestartHandler

from indy_common.authorize.auth_actions import EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from plenum.common.exceptions import RequestRejectedException
from plenum.test.freeze_ledgers.helper import sdk_send_freeze_ledgers
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.helper import build_auth_rule_request_json, sdk_send_and_check_req_json


class EditFrozenLedgersTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.trustee_wallets = [self.trustee_wallet]

    def prepare(self):
        for i in range(3):
            wallet = sdk_add_new_nym(self.looper,
                                     self.sdk_pool_handle,
                                     self.trustee_wallet,
                                     alias='trustee{}'.format(i),
                                     role=TRUSTEE_STRING)
            self.trustee_wallets.append(wallet)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        for n in self.env.txnPoolNodeSet:
            for h in n.action_manager.request_handlers.values():
                if isinstance(h, PoolRestartHandler):
                    h.restarter.handleRestartRequest = lambda *args, **kwargs: True

    def run(self):
        frozen_ledgers_ids = []

        # Step 1. Check default auth rule
        sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, self.trustee_wallets, frozen_ledgers_ids)
        with pytest.raises(RequestRejectedException):
            sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, [self.new_default_wallet], frozen_ledgers_ids)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot send txn the old way
        sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, [self.new_default_wallet], frozen_ledgers_ids)
        with pytest.raises(RequestRejectedException):
            sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, self.trustee_wallets, frozen_ledgers_ids)

        # Step 4. Check, that we can send restart action in changed way
        sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, [self.new_default_wallet], frozen_ledgers_ids)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, self.trustee_wallets, frozen_ledgers_ids)
        with pytest.raises(RequestRejectedException):
            sdk_send_freeze_ledgers(self.looper, self.sdk_pool_handle, [self.new_default_wallet], frozen_ledgers_ids)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=STEWARD)
        constraint = AuthConstraint(role=STEWARD,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=EDIT_PREFIX,
            auth_type=LEDGERS_FREEZE,
            field='*',
            old_value='*',
            new_value='*',
            constraint=constraint.as_dict
        )
