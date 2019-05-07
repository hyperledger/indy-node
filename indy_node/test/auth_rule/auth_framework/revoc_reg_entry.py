import copy
import json

import pytest

from indy_common.authorize import auth_map
from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import IDENTITY_OWNER, AuthConstraint
from indy_common.constants import REVOC_REG_ENTRY, PREV_ACCUM, VALUE, CRED_DEF_ID, REVOC_TYPE, TAG, REVOC_REG_DEF_ID, \
    ACCUM, ISSUED, REVOKED
from indy_common.state import domain
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from indy_node.test.auth_rule.auth_framework.revoc_reg_def import AddRevocRegDefTest
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from plenum.common.constants import TXN_TYPE
from plenum.common.exceptions import RequestRejectedException
from plenum.common.types import f, OPERATION
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_request_from_dict, sdk_gen_request, sdk_send_and_check
from plenum.test.pool_transactions.helper import sdk_add_new_nym


class AddRevocRegEntryTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.claim_def_req = None
        self.revoc_reg_def_req = None
        self.first_entry = None
        self.next_reg_entry = None

    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        rrd_test = AddRevocRegDefTest(self.env, auth_map.add_revoc_reg_def.get_action_id())
        rrd_test.prepare()
        self.claim_def_req = rrd_test.claim_def_req
        self.first_revoc_reg_def_req = rrd_test.send_revoc_reg_def(self.claim_def_req, wallet=self.trustee_wallet)[0][0]
        self.second_revoc_reg_def_req = rrd_test.send_revoc_reg_def(self.claim_def_req, wallet=self.trustee_wallet)[0][0]

        self.first_entry = self.build_reg_entry_req(revoc_reg_req=self.first_revoc_reg_def_req,
                                                    revoked=[1, 2, 3])
        self.next_reg_entry = self.build_reg_entry_req(revoc_reg_req=self.second_revoc_reg_def_req,
                                                       revoked=[4, 5, 6])

    def build_revoc_reg_entry_for_given_revoc_reg_def(self,
                                                      revoc_def_req):
        path = ":".join([revoc_def_req[f.IDENTIFIER.nm],
                         domain.MARKER_REVOC_DEF,
                         revoc_def_req[OPERATION][CRED_DEF_ID],
                         revoc_def_req[OPERATION][REVOC_TYPE],
                         revoc_def_req[OPERATION][TAG]])
        data = {
            REVOC_REG_DEF_ID: path,
            TXN_TYPE: REVOC_REG_ENTRY,
            REVOC_TYPE: revoc_def_req[OPERATION][REVOC_TYPE],
            VALUE: {
                PREV_ACCUM: randomString(10),
                ACCUM: randomString(10),
                ISSUED: [],
                REVOKED: [],
            }
        }
        return data

    def build_reg_entry_req(self, revoc_reg_req, revoked):
        data = self.build_revoc_reg_entry_for_given_revoc_reg_def(revoc_reg_req)
        data[VALUE][REVOKED] = revoked
        del data[VALUE][PREV_ACCUM]
        return data

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            self.send_revoc_reg_entry(data=self.first_entry, wallet=self.trustee_wallet)

        # Step 3. Check, that new auth rule is used
        self.send_revoc_reg_entry(data=self.first_entry, wallet=self.new_default_wallet)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_revoc_reg_entry(data=self.next_reg_entry, wallet=self.trustee_wallet)

    def result(self):
        pass

    def send_revoc_reg_entry(self, data, wallet=None):
        wallet = wallet if wallet else self.trustee_wallet
        req = self.build_txn_for_revoc_def_entry_by_default(wallet,
                                                            data)
        return sdk_send_and_check([json.dumps(req)], self.looper, self.env.txnPoolNodeSet, self.sdk_pool_handle)

    def build_txn_for_revoc_def_entry_by_default(self,
                                                 wallet,
                                                 data):
        req = sdk_sign_request_from_dict(self.looper, wallet, data)
        return req

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                                 auth_type=REVOC_REG_ENTRY,
                                                 field='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])


class EditRevocRegEntryTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.rre_test = None
        self.claim_def_req = None
        self.first_edit = None
        self.second_edit = None


    def prepare(self):
        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()
        self.rre_test = AddRevocRegEntryTest(self.env, auth_map.edit_revoc_reg_entry.get_action_id())
        self.rre_test.prepare()
        self.claim_def_req = self.rre_test.claim_def_req
        reg_entry = self.rre_test.first_entry

        self.first_edit = copy.deepcopy(reg_entry)
        self.second_edit = copy.deepcopy(reg_entry)
        self.rre_test.send_revoc_reg_entry(reg_entry, wallet=self.trustee_wallet)
        self.first_edit[VALUE][REVOKED] = [10, 20]
        self.first_edit[VALUE][PREV_ACCUM] = reg_entry[VALUE][ACCUM]
        self.first_edit[VALUE][ACCUM] = randomString(10)

        self.second_edit[VALUE][ACCUM] = randomString(10)
        self.second_edit[VALUE][REVOKED] = [30, 40]
        self.second_edit[VALUE][PREV_ACCUM] = self.first_edit[VALUE][ACCUM]

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, wallet=self.trustee_wallet)

        # Step 2. Check, that we cannot do txn the old way
        with pytest.raises(RequestRejectedException):
            self.rre_test.send_revoc_reg_entry(data=self.first_edit, wallet=self.trustee_wallet)

        # Step 3. Check, that new auth rule is used
        self.rre_test.send_revoc_reg_entry(data=self.first_edit, wallet=self.new_default_wallet)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, wallet=self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.rre_test.send_revoc_reg_entry(data=self.second_edit, wallet=self.trustee_wallet)

    def result(self):
        pass

    def get_changed_auth_rule(self):
        self.new_default_wallet = sdk_add_new_nym(self.looper, self.sdk_pool_handle, self.trustee_wallet, role=IDENTITY_OWNER)
        constraint = AuthConstraint(role=IDENTITY_OWNER,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                                 auth_type=REVOC_REG_ENTRY,
                                                 field='*',
                                                 old_value='*',
                                                 new_value='*',
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])