import random
from indy import ledger, did
import json

from perf_load.perf_req_gen import RequestGenerator
from perf_load.perf_utils import random_string


class RGPoolNewDemotedNode(RequestGenerator):
    _req_types = ["0"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._steward_did = None
        self._node_alias = None
        self._node_did = None

    def _rand_data(self):
        ret = "0.{}.{}.{}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return ret

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        self._node_alias = random_string(7)
        self._node_did, node_ver = await did.create_and_store_my_did(wallet_handle,
                                                                     json.dumps({'seed': random_string(32)}))
        self._steward_did, verk = await did.create_and_store_my_did(wallet_handle,
                                                                    json.dumps({'seed': random_string(32)}))

        nym_req = await ledger.build_nym_request(submitter_did, self._steward_did, verk, None, "STEWARD")
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, nym_req)

    async def _gen_req(self, submitter_did, req_data):
        data = {'alias': self._node_alias, 'client_port': 50001, 'node_port': 50002, 'node_ip': req_data,
                'client_ip': req_data, 'services': []}
        return await ledger.build_node_request(self._steward_did, self._node_did, json.dumps(data))

    def req_did(self):
        return self._steward_did
