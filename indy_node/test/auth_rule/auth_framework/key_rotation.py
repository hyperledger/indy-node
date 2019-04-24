import json

import pytest
from indy.did import replace_keys_start

from indy_common.authorize import auth_map
from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import NYM
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from indy_node.test.helper import sdk_rotate_verkey
from plenum.common.constants import TRUSTEE, VERKEY
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_gen_request, sdk_multi_sign_request_objects, sdk_send_signed_requests, \
    sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym


class RotateKeyTest(AbstractTest):
    def __init__(self, env):
        self.action_id = auth_map.key_rotation.get_action_id()
        self.action = split_action_id(self.action_id)
        self.looper = env.looper
        self.sdk_pool_handle = env.sdk_pool_handle
        self.creator_wallet = env.sdk_wallet_trustee
        self.trustee_wallet = env.sdk_wallet_trustee

        self.default_auth_rule = None
        self.changed_auth_rule = None
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
        verkey = self.sdk_modified_verkey_rotate(self.sdk_pool_handle, wh, trustee_did, client_did)

        # Step 2. Change auth rule
        self.send_and_check(self.changed_auth_rule)

        # Step 3. Check, that we cannot add new steward by old way
        sdk_rotate_verkey(self.looper, self.sdk_pool_handle, wh, trustee_did, client_did, verkey)
        verkey = self.sdk_modified_verkey_rotate(self.sdk_pool_handle, wh, client_did, client_did)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule)

        # Step 5. Check, that default auth rule works
        sdk_rotate_verkey(self.looper, self.sdk_pool_handle, wh, client_did, client_did, verkey)
        self.sdk_modified_verkey_rotate(self.sdk_pool_handle, wh, trustee_did, client_did)


    def result(self):
        pass

    def get_nym(self, role):
        wh, _ = self.creator_wallet
        did, _ = create_verkey_did(self.looper, wh)
        return self._build_nym(self.creator_wallet, role, did)

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

    def send_and_check(self, req):
        signed_reqs = sdk_multi_sign_request_objects(self.looper,
                                                     [self.creator_wallet],
                                                     [req])
        request_couple = sdk_send_signed_requests(self.sdk_pool_handle,
                                                  signed_reqs)[0]

        return sdk_get_and_check_replies(self.looper, [request_couple])[0]

    def sdk_modified_verkey_rotate(self, sdk_pool_handle, wh,
                                   did_of_changer,
                                   did_of_changed):
        verkey = self.looper.loop.run_until_complete(
            replace_keys_start(wh, did_of_changed, json.dumps({})))

        with pytest.raises(RequestRejectedException):
            sdk_add_new_nym(self.looper, sdk_pool_handle,
                            (wh, did_of_changer), dest=did_of_changed,
                            verkey=verkey)
        return verkey