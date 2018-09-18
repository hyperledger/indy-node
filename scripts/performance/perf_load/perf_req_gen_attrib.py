import json
from indy import ledger

from perf_load.perf_utils import get_txn_field
from perf_load.perf_req_gen import RequestGenerator


class RGAttrib(RequestGenerator):
    _req_types = ["100", "104"]

    async def _gen_req(self, submit_did, req_data):
        raw_attr = json.dumps({req_data: req_data})
        attr_request = await ledger.build_attrib_request(submit_did, submit_did, None, raw_attr, None)
        return attr_request

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        txn = get_txn_field(req_json)
        return txn.get('data', {}).get('raw', None)


class RGGetAttrib(RGAttrib):
    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_attrib_request(submit_did, submit_did, req_data, None, None)
        return req
