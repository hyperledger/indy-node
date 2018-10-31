import libnacl
from indy import ledger

from perf_load.perf_utils import rawToFriendly
from perf_load.perf_req_gen import RequestGenerator


class RGConfig(RequestGenerator):
    _req_types = ["111"]

    def _rand_data(self):
        raw = libnacl.randombytes(16)
        req_did = rawToFriendly(raw)
        return req_did

    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_pool_config_request(submit_did, True, False)
