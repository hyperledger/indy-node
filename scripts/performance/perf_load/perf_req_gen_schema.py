import json
import libnacl

from indy import ledger, anoncreds

from perf_load.perf_utils import rawToFriendly, get_txnid_field
from perf_load.perf_req_gen import RequestGenerator


class RGSchema(RequestGenerator):
    _req_types = ["101", "107"]

    async def _gen_req(self, submit_did, req_data):
        _, schema_json = await anoncreds.issuer_create_schema(submit_did, req_data,
                                                              "1.0", json.dumps(["name", "age", "sex", "height"]))
        schema_request = await ledger.build_schema_request(submit_did, schema_json)
        return schema_request

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        return get_txnid_field(req_json)


class RGGetSchema(RGSchema):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        target_did = rawToFriendly(raw)
        schema_marker = '02'
        name = super()._rand_data()
        version = '1.0'
        schema_id = ':'.join([target_did, schema_marker, name, version])
        return schema_id

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_schema_request(submit_did, req_data)
        return req
