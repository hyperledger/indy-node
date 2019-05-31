import json

import pytest
from indy.ledger import build_acceptance_mechanisms_request

from plenum.common.util import randomString

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_AML
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_req_obj
from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_sign_and_send_prepared_request

from indy_node.test.helper import build_auth_rule_request_json


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
        aml_req = self.taa_aml_request_module(self.trustee_wallet)
        with pytest.raises(RequestRejectedException):
            req = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                     aml_req)
            sdk_get_and_check_replies(self.looper, [req])

        # Step 3. Check, that new auth rule is used
        aml_req = self.taa_aml_request_module(self.new_default_wallet)
        req = sdk_sign_and_send_prepared_request(self.looper, self.new_default_wallet, self.sdk_pool_handle,
                                                 aml_req)
        sdk_get_and_check_replies(self.looper, [req])

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        aml_req = self.taa_aml_request_module(self.trustee_wallet)
        req = sdk_sign_and_send_prepared_request(self.looper, self.trustee_wallet, self.sdk_pool_handle,
                                                 aml_req)
        sdk_get_and_check_replies(self.looper, [req])

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet,
                                                  role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=ADD_PREFIX,
            auth_type=TXN_AUTHOR_AGREEMENT_AML,
            field='*',
            new_value='*',
            constraint=constraint.as_dict
        )

    def taa_aml_request_module(self, wallet):
        return self.looper.loop.run_until_complete(build_acceptance_mechanisms_request(
            wallet[1],
            json.dumps({
                'Nice way': 'very good way to accept agreement'}),
            randomString(), randomString()))
