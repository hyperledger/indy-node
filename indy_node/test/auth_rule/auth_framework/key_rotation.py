import json

import pytest
from indy.did import replace_keys_start

from indy_common.authorize.auth_actions import EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import NYM
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from indy_node.test.helper import sdk_rotate_verkey
from plenum.common.constants import TRUSTEE, VERKEY
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request
from plenum.test.pool_transactions.helper import sdk_add_new_nym


class RotateKeyTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.creator_wallet = env.sdk_wallet_trustee
        self.test_nym = None

    def prepare(self):
        self.test_nym = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.creator_wallet, role=None)
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        wh, client_did = self.test_nym
        _, trustee_did = self.creator_wallet

        # Step 1. Check default auth rule
        sdk_rotate_verkey(self.looper, self.sdk_pool_handle, wh, client_did, client_did)
        verkey = self.sdk_modified_verkey_rotate_failed(self.sdk_pool_handle, wh, trustee_did, client_did)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 3. Check, that we cannot add new steward by old way
        sdk_rotate_verkey(self.looper, self.sdk_pool_handle, wh, trustee_did, client_did, verkey)
        verkey = self.sdk_modified_verkey_rotate_failed(self.sdk_pool_handle, wh, client_did, client_did)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        sdk_rotate_verkey(self.looper, self.sdk_pool_handle, wh, client_did, client_did, verkey)
        self.sdk_modified_verkey_rotate_failed(self.sdk_pool_handle, wh, trustee_did, client_did)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=TRUSTEE,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=NYM,
                                                 field=VERKEY,
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.creator_wallet[1])

    def sdk_modified_verkey_rotate_failed(self, sdk_pool_handle, wh,
                                          did_of_changer,
                                          did_of_changed):
        verkey = self.looper.loop.run_until_complete(
            replace_keys_start(wh, did_of_changed, json.dumps({})))

        with pytest.raises(RequestRejectedException):
            sdk_add_new_nym(self.looper, sdk_pool_handle,
                            (wh, did_of_changer), dest=did_of_changed,
                            verkey=verkey)
        return verkey
