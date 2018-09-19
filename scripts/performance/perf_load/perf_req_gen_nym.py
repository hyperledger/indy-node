import libnacl
from indy import ledger

from perf_load.perf_utils import rawToFriendly, get_txn_field
from perf_load.perf_req_gen import RequestGenerator


class RGNym(RequestGenerator):
    _req_types = ["1", "105"]

    def _rand_data(self):
        raw = libnacl.randombytes(16)
        req_did = rawToFriendly(raw)
        return req_did

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        txn = get_txn_field(req_json)
        return txn.get('data', {}).get('dest', None)

    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_nym_request(submit_did, req_data, None, None, None)


class RGGetNym(RGNym):
    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_get_nym_request(submit_did, req_data)
