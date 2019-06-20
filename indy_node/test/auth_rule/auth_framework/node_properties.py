import random
from indy_node.test.auth_rule.auth_framework.node_services import EditNodeTest
from plenum.common.keygen_utils import init_bls_keys


class EditNodePropertiesTest(EditNodeTest):
    def __init__(self, env, action_id):
        self.node_data = None
        self.node_name = None
        self.steward_wallet = None
        super().__init__(env, action_id)

    def prepare(self):
        req, node_data, node_name, wallet = self._add_node()
        self.send_and_check(req, wallet)
        self.node_data = node_data
        self.node_name = node_name
        self.steward_wallet = wallet

        self.node_req_for_new_rule = self.get_node_req(self.trustee_wallet)
        self.node_req_1 = self.get_node_req()
        self.node_req_2 = self.get_node_req()

        self.default_auth_rule = self.get_default_auth_rule()
        self.changed_auth_rule = self.get_changed_auth_rule()

    def get_node_req(self, wallet=None):
        if None in [self.node_data, self.node_name, self.steward_wallet]:
            assert False, "Create a node before changes."
        if wallet is None:
            wallet = self.steward_wallet
        node_data = self._add_changes(self.node_data)
        req, _, _ = self._build_node(wallet,
                                     self.tconf,
                                     self.tdir,
                                     node_name=self.node_name,
                                     node_data=node_data)
        return req, wallet

    def _add_changes(self, node_data):
        pass


class EditNodeIpTest(EditNodePropertiesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        nodeIp = "127.0.0.{}".format(random.randint(1, 254))
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodePortTest(EditNodePropertiesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        nodePort = random.randint(1000, 9999)
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeClientIpTest(EditNodePropertiesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        clientIp = "127.0.0.{}".format(random.randint(1, 254))
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeClientPortTest(EditNodePropertiesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        clientPort = random.randint(1000, 9999)
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof


class EditNodeBlsTest(EditNodePropertiesTest):
    def __init__(self, env, action_id):
        super().__init__(env,
                         action_id)

    def _add_changes(self, node_data):
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = node_data
        new_blspk, key_proof = init_bls_keys(self.tdir, "node_name")
        bls_key = new_blspk
        return sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof
