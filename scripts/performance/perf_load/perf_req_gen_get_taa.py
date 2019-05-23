from indy import ledger

from perf_load.perf_req_gen import RequestGenerator


class RGGetTAA(RequestGenerator):
    _req_types = ["6"]

    def _rand_data(self):
        return '{}'

    async def _gen_req(self, submitter_did, req_data):
        return await ledger.build_get_txn_author_agreement_request(submitter_did, req_data)
