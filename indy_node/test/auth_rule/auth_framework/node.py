import copy
import json
import random
from abc import ABCMeta, abstractmethod
from typing import Optional, Any, NamedTuple

import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, split_action_id, AuthActionAdd, AuthActionEdit, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE, IDENTITY_OWNER, AbstractAuthConstraint, ConstraintsEnum, \
    accepted_roles, AuthConstraint
from indy_common.constants import NYM, TRUST_ANCHOR, TRUST_ANCHOR_STRING, NETWORK_MONITOR_STRING, NETWORK_MONITOR, NODE
from indy_node.test.auth_rule.auth_framework.basic import AbstractTest, roles_to_string
from indy_node.test.auth_rule.helper import create_verkey_did, generate_auth_rule_operation
from plenum.common.constants import STEWARD_STRING, STEWARD, TRUSTEE, TRUSTEE_STRING, IDENTITY_OWNER_STRING, VALIDATOR, \
    SERVICES
from plenum.common.exceptions import RequestRejectedException
from plenum.common.keygen_utils import init_bls_keys
from plenum.common.util import randomString
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies, \
    sdk_json_to_request_object, sdk_multi_sign_request_objects, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import prepare_nym_request, sdk_add_new_node, sdk_add_new_nym, \
    sdk_add_new_steward_and_node, sdk_send_update_node
from indy_common.authorize import auth_map
from plenum.test.testing_utils import FakeSomething
from stp_core.network.port_dispenser import genHa

nodeCount = 7


class NodeAuthTest(AbstractTest, metaclass=ABCMeta):
    def __init__(self, env, action):
        self.looper = env.looper
        self.tconf = env.tconf
        self.tdir = env.tdir
        self.sdk_pool_handle = env.sdk_pool_handle
        self.client_wallet = env.sdk_wallet_client
        self.trustee_wallet = self._create_trustee(env.sdk_wallet_trustee)
        self.action = action
        self.action_id = self.action.get_action_id()
        self.nodes = env.nodes
        self.new_nodes = {}

    def prepare(self):
        self.node_req_1 = self.get_node_req()
        self.node_req_2 = self.get_node_req()

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def run(self):
        
        # Step 1. Change auth rule
        self.send_and_check(self.changed_auth_rule, self.trustee_wallet)

        # Step 2. Check, that we cannot send NODE txn by old way
        with pytest.raises(RequestRejectedException):
            rep = self.send_and_check(*self.node_req_1)

        # Step 3. Check, that a new way works
        self.send_and_check(self.node_req_for_new_rule, self.trustee_wallet)

        # Step 4. Return default auth rule
        self.send_and_check(self.default_auth_rule, self.trustee_wallet)

        # Step 5. Check, that default auth rule works
        self.send_and_check(*self.node_req_2)

        self._demote_new_nodes()

    def result(self):
        pass

    def send_and_check(self, req, wallet):
        signed_reqs = sdk_multi_sign_request_objects(self.looper,
                                                     [wallet],
                                                     [req])
        request_couple = sdk_send_signed_requests(self.sdk_pool_handle,
                                                  signed_reqs)[0]

        return sdk_get_and_check_replies(self.looper,
                                         [request_couple],
                                         timeout=100)[0]

    def get_node_req(self, steward_wallet=None):
        pass

    def get_changed_auth_rule(self):
        constraint = AuthConstraint(role=TRUSTEE,
                                    sig_count=1,
                                    need_to_be_owner=False)
        operation = self._get_auth_rule_operation(constraint)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def get_default_auth_rule(self):
        constraint = auth_map.auth_map.get(self.action_id)
        operation = self._get_auth_rule_operation(constraint)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def _create_steward(self):
        return sdk_add_new_nym(self.looper, self.sdk_pool_handle,
                               self.trustee_wallet,
                               role=STEWARD_STRING)

    def _create_trustee(self, trustee_wallet):
        return sdk_add_new_nym(self.looper, self.sdk_pool_handle,
                               trustee_wallet,
                               role=TRUSTEE_STRING)
        # wh, _ = self.trustee_wallet
        # did, verkey = create_verkey_did(self.looper, wh)
        # req = self._build_nym(self.trustee_wallet, STEWARD_STRING, did)
        # self.send_and_check(req, self.trustee_wallet)
        # return did, verkey

    def _add_node(self, wallet=None, services=[VALIDATOR]):
        if not wallet:
            wallet = self._create_steward()
        req, node_data, node_name = self._build_node(wallet,
                                                     self.tconf,
                                                     self.tdir,
                                                     services=services)
        self.new_nodes[wallet] = (node_data, node_name)
        return req, node_data, node_name, wallet

    def _edit_node(self, wallet=None, services=[VALIDATOR]):
        req, node_data, node_name, wallet = self._add_node(wallet)
        self.send_and_check(req, wallet)
        node_data = self._add_changes(node_data)
        req, node_data, node_name = self._build_node(wallet,
                                                     self.tconf,
                                                     self.tdir,
                                                     services=services,
                                                     node_name=node_name,
                                                     node_data=node_data)
        return req, node_data, node_name, wallet

    def _get_auth_rule_operation(self, constraint):
        pass

    def _demote_new_nodes(self):
        for wallet, (node_data, node_name) in self.new_nodes.items():
            req1, node_data1, node_name1 = self._build_node(wallet,
                                                            self.tconf,
                                                            self.tdir,
                                                            services=[],
                                                            node_name=node_name,
                                                            node_data=node_data)
            self.send_and_check(req1, wallet)
            sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
            # sdk_send_update_node(self.looper, wallet, self.sdk_pool_handle,
            #                      sigseed, node_name, None, None, None, None,
            #                      services=[])

    def _add_changes(self, node_data):
        return node_data


class AddNodeTest(NodeAuthTest):
    def __init__(self, env, field, new_value):
        action = AuthActionAdd(NODE, field, value=new_value)
        super().__init__(env,
                         action=action)

    def prepare(self):
        super().prepare()
        self.node_req_for_new_rule, _ = self.get_node_req(self.trustee_wallet)

    def get_node_req(self, steward_wallet=None):
        req, node_data, node_name, wallet = self._add_node(steward_wallet)
        return req, wallet

    def _get_auth_rule_operation(self, constraint):
        return generate_auth_rule_operation(auth_action=ADD_PREFIX,
                                            auth_type=NODE,
                                            field=self.action.field,
                                            new_value=self.action.value,
                                            constraint=constraint.as_dict)


class EditNodeTest(NodeAuthTest):
    def __init__(self, env, field, old_value, new_value, new_services=[VALIDATOR]):
        action = AuthActionEdit(NODE, field, old_value=old_value, new_value=new_value)
        self.new_services = new_services
        super().__init__(env,
                         action=action)

    def prepare(self):
        self.node_req_2 = self.get_node_req()

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

        req, node_data, node_name, wallet = self._add_node()
        self.send_and_check(req, wallet)
        node_data = self._add_changes(node_data)
        self.node_req_for_new_rule, _, _ = self._build_node(self.trustee_wallet,
                                                            self.tconf,
                                                            self.tdir,
                                                            services=self.new_services,
                                                            node_name=node_name,
                                                            node_data=node_data)

        node_data = self._add_changes(node_data)
        req, node_data, node_name = self._build_node(wallet,
                                                     self.tconf,
                                                     self.tdir,
                                                     services=self.new_services,
                                                     node_name=node_name,
                                                     node_data=node_data)
        self.node_req_1 = req, wallet

    def get_node_req(self, steward_wallet=None):
        req, node_data, node_name, wallet = self._edit_node(steward_wallet, )
        return req, wallet

    def _get_auth_rule_operation(self, constraint):
        return generate_auth_rule_operation(auth_action=EDIT_PREFIX,
                                            auth_type=NODE,
                                            field=self.action.field,
                                            new_value=self.action.new_value,
                                            old_value=self.action.old_value,
                                            constraint=constraint.as_dict)


class AddNewNodeTest(AddNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field=SERVICES,
                         new_value=[VALIDATOR])


class AddNewNodeEmptyServiceTest(AddNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field=SERVICES,
                         new_value=[])

    def _add_node(self, wallet=None, services=[VALIDATOR]):
        return super()._add_node(wallet, services=[])

    def _demote_new_nodes(self):
        pass


class DemoteNodeTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field=SERVICES,
                         old_value=[VALIDATOR],
                         new_value=[],
                         new_services=[])
    #
    # def prepare(self):
    #     super().prepare()
    #     req, node_data, node_name, wallet = self._add_node()
    #     self.send_and_check(req, wallet)
    #     self.node_req_for_new_rule, _, _ = self._build_node(self.trustee_wallet,
    #                                                         self.tconf,
    #                                                         self.tdir,
    #                                                         node_name=node_name,
    #                                                         node_data=node_data,
    #                                                         services=[])

    def _edit_node(self, wallet=None, services=[VALIDATOR]):
        return super()._edit_node(wallet=None, services=[])

    def _demote_new_nodes(self):
        pass


class PromoteNodeTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field=SERVICES,
                         old_value=[],
                         new_value=[VALIDATOR])

    def _add_node(self, wallet=None, services=[VALIDATOR]):
        return super()._add_node(wallet, services=[])


class EditNodeIpTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field="node_ip",
                         old_value="*",
                         new_value="*")

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        nodeIp = "127.0.0.{}".format(random.randint(1, 254))
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodePortTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field="node_port",
                         old_value="*",
                         new_value="*")

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        nodePort = random.randint(1000, 9999)
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeClientIpTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field="client_ip",
                         old_value="*",
                         new_value="*")

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        clientIp = "127.0.0.{}".format(random.randint(1, 254))
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeClientPortTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field="client_port",
                         old_value="*",
                         new_value="*")

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        clientPort = random.randint(1000, 9999)
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeBlsTest(EditNodeTest):
    def __init__(self, env):
        super().__init__(env,
                         field="blskey",
                         old_value="*",
                         new_value="*")

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        new_blspk, key_proof = init_bls_keys(self.tdir, "node_name")
        bls_key = new_blspk
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class TestAuthRuleUsing():
    map_of_tests = {
        auth_map.adding_new_node.get_action_id(): AddNewNodeTest,
        auth_map.adding_new_node_with_empty_services.get_action_id(): AddNewNodeEmptyServiceTest,
        auth_map.demote_node.get_action_id(): DemoteNodeTest,
        auth_map.promote_node.get_action_id(): PromoteNodeTest,
        auth_map.change_node_ip.get_action_id(): EditNodeIpTest,
        auth_map.change_node_port.get_action_id(): EditNodePortTest,
        auth_map.change_client_ip.get_action_id(): EditNodeClientIpTest,
        auth_map.change_client_port.get_action_id(): EditNodeClientPortTest,
        auth_map.change_bls_key.get_action_id(): EditNodeBlsTest,
    }

    @pytest.fixture(scope="module")
    def env(self,
            looper,
            tconf,
            tdir,
            sdk_pool_handle,
            sdk_wallet_trustee,
            sdk_wallet_steward,
            sdk_wallet_trust_anchor,
            sdk_wallet_client,
            txnPoolNodeSet):
        role_to_wallet = {
            TRUSTEE: sdk_wallet_trustee,
            STEWARD: sdk_wallet_steward,
            TRUST_ANCHOR: sdk_wallet_trust_anchor,
            IDENTITY_OWNER: sdk_wallet_client,
        }
        return FakeSomething(looper=looper,
                             sdk_pool_handle=sdk_pool_handle,
                             tconf=tconf,
                             tdir=tdir,
                             nodes=txnPoolNodeSet,
                             sdk_wallet_trustee=sdk_wallet_trustee,
                             sdk_wallet_steward=sdk_wallet_steward,
                             sdk_wallet_client=sdk_wallet_client,
                             role_to_wallet=role_to_wallet)

    @pytest.fixture(scope='module', params=[(k, v) for k, v in map_of_tests.items()])
    def auth_rule_tests(self, request, env):
        action_id, test_cls = request.param
        test = test_cls(env)
        return action_id, test

    def test_auth_rule_using(self, auth_rule_tests):
        descr, test = auth_rule_tests
        print("Running test: {}".format(descr))
        test.prepare()
        test.run()
        test.result()
