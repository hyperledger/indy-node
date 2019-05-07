import json
import random
from abc import ABCMeta, abstractmethod

from indy_common.authorize.auth_actions import EDIT_PREFIX, split_action_id
from indy_common.authorize.auth_map import auth_map
from indy_common.constants import TRUST_ANCHOR, NETWORK_MONITOR, NETWORK_MONITOR_STRING, TRUST_ANCHOR_STRING
from indy_node.test.auth_rule.helper import generate_auth_rule_operation
from plenum.common.constants import TRUSTEE, TRUSTEE_STRING, STEWARD_STRING, STEWARD, IDENTITY_OWNER, \
    IDENTITY_OWNER_STRING, VALIDATOR
from plenum.common.util import randomString
from plenum.test.helper import sdk_json_to_request_object, sdk_gen_request, sdk_sign_request_objects, \
    sdk_send_signed_requests, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import prepare_nym_request
from plenum.test.helper import sdk_json_to_request_object, sdk_gen_request
from plenum.test.pool_transactions.helper import prepare_nym_request, prepare_new_node_data, prepare_node_request

roles_to_string = {
    TRUSTEE: TRUSTEE_STRING,
    STEWARD: STEWARD_STRING,
    TRUST_ANCHOR: TRUST_ANCHOR_STRING,
    NETWORK_MONITOR: NETWORK_MONITOR_STRING,
    IDENTITY_OWNER: '',
    '': '',
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


class AuthTest(AbstractTest):

    def __init__(self, env, action_id):
        self.looper = env.looper
        self.action_id = action_id
        self.action = split_action_id(action_id)
        self.sdk_pool_handle = env.sdk_pool_handle
        self.trustee_wallet = env.sdk_wallet_trustee
        self.env = env

        self.default_auth_rule = None
        self.changed_auth_rule = None
        self.new_default_wallet = None

    def _build_nym(self, creator_wallet, role_string, did, verkey=None, skipverkey=True):
        seed = randomString(32)
        alias = randomString(5)
        nym_request, new_did = self.looper.loop.run_until_complete(
            prepare_nym_request(creator_wallet,
                                seed,
                                alias,
                                role_string,
                                dest=did,
                                verkey=verkey,
                                skipverkey=skipverkey))
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
        constraint = auth_map.get(self.action_id)
        operation = generate_auth_rule_operation(auth_action=self.action.prefix,
                                                 auth_type=self.action.txn_type,
                                                 field=self.action.field,
                                                 old_value=self.action.old_value if self.action.prefix == EDIT_PREFIX else None,
                                                 new_value=self.action.new_value,
                                                 constraint=constraint.as_dict)
        return sdk_gen_request(operation, identifier=self.trustee_wallet[1])

    def send_and_check(self, req, wallet):
        signed_reqs = sdk_sign_request_objects(self.looper,
                                               wallet,
                                               [req])
        request_couple = sdk_send_signed_requests(self.sdk_pool_handle,
                                                  signed_reqs)[0]

        return sdk_get_and_check_replies(self.looper,
                                         [request_couple])[0]
