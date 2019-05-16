import pytest
from plenum.common.util import randomString

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_AML
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_get_and_check_replies, sdk_sign_and_submit_req_obj
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.txn_author_agreement.conftest import taa_aml_request_module


class TxnAuthorAgreementAMLTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.aml_request = None

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        aml_req = taa_aml_request_module(self.looper, self.trustee_wallet, None)
        with pytest.raises(RequestRejectedException):
            sdk_get_and_check_replies(self.looper, [
                sdk_sign_and_submit_req_obj(self.looper, self.sdk_pool_handle, self.trustee_wallet, aml_req)])

        # Step 3. Check, that new auth rule is used
        aml_req = taa_aml_request_module(self.looper, self.new_default_wallet, None)
        sdk_get_and_check_replies(self.looper, [
            sdk_sign_and_submit_req_obj(self.looper, self.sdk_pool_handle, self.new_default_wallet, aml_req)])

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        aml_req = taa_aml_request_module(self.looper, self.trustee_wallet, None)
        sdk_get_and_check_replies(self.looper, [
            sdk_sign_and_submit_req_obj(self.looper, self.sdk_pool_handle, self.trustee_wallet, aml_req)])

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                                                  role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=TXN_AUTHOR_AGREEMENT_AML,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])
