import json

import pytest
from indy.ledger import build_get_schema_request, parse_get_schema_response

from indy_common.state.domain import make_state_path_for_claim_def
from plenum.common.types import OPERATION
from plenum.common.util import randomString

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd, AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint, IDENTITY_OWNER
from indy_common.constants import CLAIM_DEF, ID, REVOC_TYPE, TAG, CRED_DEF_ID, VALUE, ISSUANCE_TYPE, MAX_CRED_NUM, \
    TAILS_HASH, TAILS_LOCATION, PUBLIC_KEYS, ISSUANCE_BY_DEFAULT, REVOC_REG_DEF, CLAIM_DEF_SCHEMA_REF, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG
from indy_node.test.anon_creds.conftest import send_revoc_reg_def_by_default
from indy_node.test.api.helper import sdk_write_schema
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, AuthTest
from indy_node.test.claim_def.test_send_claim_def import sdk_send_claim_def
from plenum.common.constants import TRUSTEE, TXN_TYPE
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_get_and_check_replies, \
    sdk_multi_sign_request_objects, sdk_send_signed_requests, sdk_sign_and_submit_req, sdk_get_reply, \
    sdk_sign_request_from_dict, sdk_send_and_check, sdk_sign_and_submit_op
from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_sign_and_send_prepared_request
from indy_common.authorize import auth_map

from indy_node.test.helper import build_auth_rule_request_json


def get_schema_json(looper, sdk_pool_handle, sdk_wallet_trustee):
    wallet_handle, identifier = sdk_wallet_trustee
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))
    return schema_json


class AddRevocRegDefTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.claim_def_req = None

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.claim_def_req = self.get_claim_def()[0][0]

    def run(self):

        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            self.send_revoc_reg_def(self.claim_def_req, wallet=self.trustee_wallet)

        # Step 3. Check, that new auth rule is used
        self.send_revoc_reg_def(self.claim_def_req, wallet=self.new_default_wallet)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_revoc_reg_def(self.claim_def_req, wallet=self.trustee_wallet)

    def result(self):
        pass

    def get_claim_def(self):
        schema_json = get_schema_json(self.looper, self.sdk_pool_handle, self.trustee_wallet)
        return sdk_send_claim_def(self.looper, self.sdk_pool_handle, self.trustee_wallet, 'tag' + randomString(4),
                                  schema_json)

    def send_revoc_reg_def(self, claim_def_req=None, author_did=None, wallet=None, revoc_reg_def=None):
        claim_def_req = claim_def_req if claim_def_req else self.claim_def_req
        wallet = wallet or self.trustee_wallet
        req = revoc_reg_def if revoc_reg_def else self.build_revoc_def_by_default(claim_def_req,
                                                                                  author_did=author_did,
                                                                                  wallet=wallet)
        return sdk_send_and_check([json.dumps(req)], self.looper, self.env.txnPoolNodeSet, self.sdk_pool_handle)

    def build_revoc_def_by_default(self, claim_def_req, author_did=None, wallet=None, req_def_id=None):
        wallet = wallet if wallet else self.trustee_wallet
        author_did = author_did if author_did else self.trustee_wallet[1]
        data = {
            ID: req_def_id if req_def_id else randomString(50),
            TXN_TYPE: REVOC_REG_DEF,
            REVOC_TYPE: "CL_ACCUM",
            TAG: randomString(5),
            CRED_DEF_ID: make_state_path_for_claim_def(author_did,
                                                       str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                                       claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                                       claim_def_req['operation'][CLAIM_DEF_TAG]
                                                       ).decode(),
            VALUE: {
                ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
                MAX_CRED_NUM: 1000000,
                TAILS_HASH: randomString(50),
                TAILS_LOCATION: 'http://tails.location.com',
                PUBLIC_KEYS: {},
            }
        }
        req = sdk_sign_request_from_dict(self.looper, wallet, data)
        return req

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=ADD_PREFIX,
            auth_type=REVOC_REG_DEF,
            field='*',
            new_value='*',
            constraint=constraint.as_dict
        )


class EditRevocRegDefTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.revoc_reg_def_trustee = None
        self.revoc_reg_def_new = None
        self.add_revoc_reg_def = AddRevocRegDefTest(env, auth_map.add_revoc_reg_def.get_action_id())
        self.add_revoc_reg_def.prepare()

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.revoc_reg_def_trustee = self.add_revoc_reg_def.send_revoc_reg_def()[0][0]
        self.add_revoc_reg_def.send_and_check(self.add_revoc_reg_def.changed_auth_rule, self.trustee_wallet)
        self.revoc_reg_def_new = self.add_revoc_reg_def.send_revoc_reg_def(wallet=self.new_default_wallet)[0][0]

    def do_edit_revoc_reg_def(self, origin_rrd_req, wallet):
        origin_rrd_req[OPERATION][VALUE][TAILS_HASH] = randomString(20)
        resp = sdk_sign_and_submit_op(self.looper, self.sdk_pool_handle, wallet, op=origin_rrd_req[OPERATION])
        sdk_get_and_check_replies(self.looper, [resp])

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            self.do_edit_revoc_reg_def(self.revoc_reg_def_trustee, wallet=self.trustee_wallet)

        # Step 3. Check, that new auth rule is used
        self.do_edit_revoc_reg_def(self.revoc_reg_def_new, self.new_default_wallet)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.do_edit_revoc_reg_def(self.revoc_reg_def_trustee, self.trustee_wallet)

        self.teardown_for_add()

    def teardown_for_add(self):
        self.add_revoc_reg_def.send_and_check(self.add_revoc_reg_def.default_auth_rule, self.trustee_wallet)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = self.add_revoc_reg_def.new_default_wallet
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1],
            auth_action=EDIT_PREFIX,
            auth_type=REVOC_REG_DEF,
            field='*',
            old_value='*',
            new_value='*',
            constraint=constraint.as_dict
        )
