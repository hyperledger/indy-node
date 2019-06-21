import pytest

from indy_node.server.request_handlers.action_req_handlers.validator_info_handler import ValidatorInfoHandler
from indy_node.test.validator_info.helper import sdk_get_validator_info

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import VALIDATOR_INFO
from plenum.common.exceptions import RequestRejectedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.testing_utils import FakeSomething

from indy_node.test.helper import build_auth_rule_request_json
from indy_node.test.auth_rule.auth_framework.basic import AuthTest


class ValidatorInfoTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        for n in self.env.txnPoolNodeSet:
            info_tool = FakeSomething(
                info={},
                memory_profiler={},
                _generate_software_info=lambda *args, **kwargs: {},
                extractions={},
                node_disk_size={}
            )
            for h in n.action_manager.request_handlers.values():
                if isinstance(h, ValidatorInfoHandler):
                    h.info_tool = info_tool

    def run(self):
        # Step 1. Check default auth rule
        sdk_get_validator_info(self.looper, self.trustee_wallet, self.sdk_pool_handle)
        with pytest.raises(RequestRejectedException):
            sdk_get_validator_info(self.looper, self.new_default_wallet, self.sdk_pool_handle)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 3. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            sdk_get_validator_info(self.looper, self.trustee_wallet, self.sdk_pool_handle)

        # Step 4. Check, that new auth rule is used
        sdk_get_validator_info(self.looper, self.new_default_wallet, self.sdk_pool_handle)

        # Step 5. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 6. Check, that default auth rule works
        sdk_get_validator_info(self.looper, self.trustee_wallet, self.sdk_pool_handle)
        with pytest.raises(RequestRejectedException):
            sdk_get_validator_info(self.looper, self.new_default_wallet, self.sdk_pool_handle)

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
            auth_type=VALIDATOR_INFO,
            field='*',
            new_value='*',
            constraint=constraint.as_dict
        )
