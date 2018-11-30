import random
from indy import ledger

from perf_load.perf_req_gen import RequestGenerator


class RGConfigChangeState(RequestGenerator):
    _req_types = ["111"]

    def _rand_data(self):
        return str(random.randint(0, 99999999))

    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_pool_config_request(submit_did, True, False)
