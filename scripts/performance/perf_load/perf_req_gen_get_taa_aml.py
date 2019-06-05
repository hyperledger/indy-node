from indy import ledger

from perf_load.perf_req_gen import RequestGenerator


class RGGetTAAAML(RequestGenerator):
    _req_types = ["7"]

    def _rand_data(self):
        return (None, None)

    async def _gen_req(self, submitter_did, req_data):
        return await ledger.build_get_acceptance_mechanisms_request(submitter_did, req_data[0], req_data[1])
