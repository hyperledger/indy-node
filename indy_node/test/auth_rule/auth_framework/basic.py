import json
import random
from abc import ABCMeta, abstractmethod

from indy_common.authorize.auth_map import auth_map
from indy_common.constants import TRUST_ANCHOR, NETWORK_MONITOR, NETWORK_MONITOR_STRING, TRUST_ANCHOR_STRING
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from plenum.common.constants import TRUSTEE, TRUSTEE_STRING, STEWARD_STRING, STEWARD, IDENTITY_OWNER, \
    IDENTITY_OWNER_STRING, VALIDATOR
from plenum.common.util import randomString
from plenum.test.helper import sdk_json_to_request_object, sdk_gen_request
from plenum.test.pool_transactions.helper import prepare_nym_request, prepare_new_node_data, prepare_node_request

roles_to_string = {
    TRUSTEE: TRUSTEE_STRING,
    STEWARD: STEWARD_STRING,
    TRUST_ANCHOR: TRUST_ANCHOR_STRING,
    NETWORK_MONITOR: NETWORK_MONITOR_STRING,
    IDENTITY_OWNER: IDENTITY_OWNER_STRING,
}


class AbstractTest(metaclass=ABCMeta):
    action_id = ""

    @abstractmethod
    def prepare(self):
        pass


    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def result(self):
        pass

    def _build_nym(self, creator_wallet, role_string, did):
        seed = randomString(32)
        alias = randomString(5)
        nym_request, new_did = self.looper.loop.run_until_complete(
            prepare_nym_request(creator_wallet,
                                seed,
                                alias,
                                role_string,
                                dest=did))
        return sdk_json_to_request_object(json.loads(nym_request))

    def _build_node(self, steward_wallet_handle, tconf, tdir, services=[VALIDATOR],
                    node_name=None, node_data=None):
        if not node_name:
            node_name = randomString(10)
            print(node_name)
        sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = \
            prepare_new_node_data(tconf, tdir, node_name) if not node_data else node_data

        # filling node request
        _, steward_did = steward_wallet_handle
        node_request = self.looper.loop.run_until_complete(
            prepare_node_request(steward_did,
                                 new_node_name=node_name,
                                 clientIp=clientIp,
                                 clientPort=clientPort,
                                 nodeIp=nodeIp,
                                 nodePort=nodePort,
                                 bls_key=bls_key,
                                 sigseed=sigseed,
                                 services=services,
                                 key_proof=key_proof))
        node_data = sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof
        return sdk_json_to_request_object(json.loads(node_request)), node_data, node_name

    def get_default_auth_rule(self):
        constraint = auth_map.auth_map.get(self.action_id)
        operation = generate_auth_rule_operation(auth_action=self.action_def.prefix,
                                                 auth_type=self.action_def.txn_type,
                                                 field=self.action_def.field,
                                                 old_value=self.action_def.old_value,
                                                 new_value=self.action_def.new_value,
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])


class AbstractRoleTest(AbstractTest, metaclass=ABCMeta):
    def __init__(self, role, env):
        self.role = role
        self.looper = None

    @abstractmethod
    def compile_local_map(self):
        pass