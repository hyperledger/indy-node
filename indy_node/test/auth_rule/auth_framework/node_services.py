import pytest
from abc import abstractmethod

from plenum.test.test_node import ensureElectionsDone

from indy_common.authorize.auth_actions import split_action_id
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_node.test.auth_rule.auth_framework.basic import AuthTest
from plenum.common.constants import STEWARD_STRING, TRUSTEE, TRUSTEE_STRING, VALIDATOR
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import waitForViewChange
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.helper import build_auth_rule_request_json
from stp_core.loop.eventually import eventually


class NodeAuthTest(AuthTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.tconf = env.tconf
        self.tdir = env.tdir
        self.sdk_pool_handle = env.sdk_pool_handle
        self.client_wallet = env.sdk_wallet_client
        self.trustee_wallet = self._create_trustee(env.sdk_wallet_trustee)
        self.new_nodes = {}
        self.txnPoolNodeSet = env.txnPoolNodeSet

    def prepare(self):
        pass

    def run(self):

        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 2. Check, that we cannot send NODE txn by old way
        with pytest.raises(RequestRejectedException):
            self.send_and_check(*self.node_req_1)

        # Step 3. Check, that a new way works
        self.send_and_check(*self.node_req_for_new_rule)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_and_check(*self.node_req_2)

        self._demote_new_nodes()

    def result(self):
        pass

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=TRUSTEE,
                                    sig_count=1,
                                    need_to_be_owner=False)
        params = self._generate_auth_rule_params(constraint)
        return build_auth_rule_request_json(
            self.looper, self.trustee_wallet[1], **params
        )

    def _create_steward(self):
        return sdk_add_new_nym(self.looper, self.sdk_pool_handle,
                               self.trustee_wallet,
                               role=STEWARD_STRING)

    def _create_trustee(self, trustee_wallet):
        return sdk_add_new_nym(self.looper, self.sdk_pool_handle,
                               trustee_wallet,
                               role=TRUSTEE_STRING)

    def _add_node(self, wallet=None, services=[VALIDATOR]):
        if not wallet:
            wallet = self._create_steward()
        req, node_data, node_name = self._build_node(wallet,
                                                     self.tconf,
                                                     self.tdir,
                                                     services=services)
        self.new_nodes[wallet] = (node_data, node_name)
        return req, node_data, node_name, wallet

    def _demote_new_nodes(self):
        view_no = self.txnPoolNodeSet[0].viewNo
        for wallet, (node_data, node_name) in self.new_nodes.items():
            print("demote {}".format(node_name))
            req1, node_data1, node_name1 = self._build_node(wallet,
                                                            self.tconf,
                                                            self.tdir,
                                                            services=[],
                                                            node_name=node_name,
                                                            node_data=node_data)
            self.send_and_check(req1, wallet)
            view_no = self._wait_view_change_finish(view_no)

    def _wait_view_change_finish(self, view_no):
        view_no += 1
        waitForViewChange(looper=self.looper, txnPoolNodeSet=self.txnPoolNodeSet,
                          expectedViewNo=view_no)

        def check_not_in_view_change():
            assert all([not n.master_replica._consensus_data.waiting_for_new_view
                        for n in self.txnPoolNodeSet])

        # we may have multiple view changes since we can select the same Primary as in previous view,
        # or select a demoted node as a Primary
        self.looper.run(eventually(check_not_in_view_change, timeout=100))
        return view_no

    @abstractmethod
    def _generate_auth_rule_params(self, constraint):
        pass


class AddNodeTest(NodeAuthTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id=action_id)

    def prepare(self):
        self.node_req_1 = self.get_node_req()
        self.new_nodes.pop(self.node_req_1[1])
        self.node_req_2 = self.get_node_req()
        self.node_req_for_new_rule = self.get_node_req(self.trustee_wallet)

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def get_node_req(self, steward_wallet=None):
        req, node_data, node_name, wallet = self._add_node(steward_wallet)
        return req, wallet

    def _generate_auth_rule_params(self, constraint):
        return dict(
            auth_action=self.action.prefix,
            auth_type=self.action.txn_type,
            field=self.action.field,
            new_value=self.action.new_value,
            constraint=constraint.as_dict
        )


class EditNodeTest(NodeAuthTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id=action_id)

    def _generate_auth_rule_params(self, constraint):
        return dict(
            auth_action=self.action.prefix,
            auth_type=self.action.txn_type,
            field=self.action.field,
            new_value=self.action.new_value,
            old_value=self.action.old_value,
            constraint=constraint.as_dict
        )


class EditNodeServicesTest(EditNodeTest):
    def __init__(self, env, action_id):
        super().__init__(env, action_id)
        self.new_services = self.action.new_value

    def prepare(self):
        req, node_data, node_name, wallet = self._edit_node()
        self.node_req_1 = req, wallet

        req, node_data, node_name, wallet = self._edit_node(node_name=node_name,
                                                            node_data=node_data,
                                                            wallet=self.trustee_wallet)
        self.node_req_for_new_rule = req, self.trustee_wallet

        req, node_data, node_name, wallet = self._edit_node()
        self.node_req_2 = req, wallet

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 2. Check, that we cannot send NODE txn by old way
        with pytest.raises(RequestRejectedException):
            self.send_and_check(*self.node_req_1)

        view_no = self.txnPoolNodeSet[0].viewNo

        # Step 3. Check, that a new way works
        self.send_and_check(*self.node_req_for_new_rule)

        view_no = self._wait_view_change_finish(view_no)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_and_check(*self.node_req_2)

        view_no = self._wait_view_change_finish(view_no)

        self._demote_new_nodes()

    def _edit_node(self, wallet=None, services=[VALIDATOR], node_name=None, node_data=None):
        if not (node_name and node_data and wallet):
            req, node_data, node_name, wallet = self._add_node()
            self.send_and_check(req, wallet)
        req, node_data, node_name = self._build_node(wallet,
                                                     self.tconf,
                                                     self.tdir,
                                                     services=services,
                                                     node_name=node_name,
                                                     node_data=node_data)
        return req, node_data, node_name, wallet


class AddNewNodeTest(AddNodeTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def run(self):
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 2. Check, that we cannot send NODE txn by old way
        with pytest.raises(RequestRejectedException):
            self.send_and_check(*self.node_req_1)

        prev_view_no = self.txnPoolNodeSet[0].viewNo
        new_node_count = len(self.new_nodes)

        # Step 3. Check, that a new way works
        self.send_and_check(*self.node_req_for_new_rule)

        prev_view_no = self._wait_view_change_finish(prev_view_no)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_and_check(*self.node_req_2)

        prev_view_no = self._wait_view_change_finish(prev_view_no)

        self._demote_new_nodes()


class AddNewNodeEmptyServiceTest(AddNodeTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_node(self, wallet=None, services=[]):
        return super()._add_node(wallet, services)

    def _demote_new_nodes(self):
        # Pass demote_new_nodes because in this test
        # all nodes create with service=[]
        pass


class DemoteNodeTest(EditNodeServicesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _edit_node(self, wallet=None, services=[], node_name=None, node_data=None):
        return super()._edit_node(wallet, services, node_name, node_data)

    def _demote_new_nodes(self):
        pass


class PromoteNodeTest(EditNodeServicesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_node(self, wallet=None, services=[]):
        return super()._add_node(wallet, services)
