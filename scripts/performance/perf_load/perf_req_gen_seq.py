import random
from perf_load.perf_req_gen import RequestGenerator


class RGSeqReqs(RequestGenerator):
    def __init__(self, *args, reqs=list(), next_random: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._req_idx = -1
        self._next_idx = self._rand_idx if next_random else self._seq_idx
        if not isinstance(reqs, list):
            raise RuntimeError("Bad Requests sequence provided")
        self._reqs_collection = []
        for reqc, prms in reqs:
            if not issubclass(reqc, RequestGenerator):
                raise RuntimeError("Bad Request class provided")
            param = {}
            if isinstance(prms, int) and prms > 0:
                cnt = prms
            elif isinstance(prms, dict):
                cnt = prms.get('count', 1)
                param = prms
            else:
                raise RuntimeError("Bad Request params provided")
            new_req = reqc(*args, **param, **kwargs)
            for i in range(0, cnt):
                self._reqs_collection.append(new_req)
        if len(self._reqs_collection) == 0:
            raise RuntimeError("At least one class should be provided")

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        for req_builder in set(self._reqs_collection):
            await req_builder.on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)

    def _seq_idx(self):
        return (self._req_idx + 1) % len(self._reqs_collection)

    def _rand_idx(self):
        return random.randint(0, len(self._reqs_collection) - 1)

    def _gen_req_data(self):
        self._req_idx = self._next_idx()
        return self._reqs_collection[self._req_idx]._gen_req_data()

    def get_label(self):
        return self._reqs_collection[self._req_idx].get_label()

    async def _gen_req(self, submit_did, req_data):
        req_gen = self._reqs_collection[self._req_idx]
        return await req_gen._gen_req(submit_did, req_data)

    async def on_request_generated(self, req_data, gen_req):
        for r in self._reqs_collection:
            await r.on_request_generated(req_data, gen_req)

    async def on_request_replied(self, req_data, req, resp_or_exp):
        for r in self._reqs_collection:
            await r.on_request_replied(req_data, req, resp_or_exp)

    def req_did(self):
        return self._reqs_collection[self._req_idx].req_did()
