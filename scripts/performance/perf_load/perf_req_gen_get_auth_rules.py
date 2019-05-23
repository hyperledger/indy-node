from indy import ledger

from perf_load.perf_req_gen import RequestGenerator


class RGGetAuthRules(RequestGenerator):
    _req_types = ["121"]

    def _rand_data(self):
        return ('102', 'ADD', '*', '*')

    async def _gen_req(self, submitter_did, req_data):
        return await ledger.build_get_auth_rule_request(submitter_did, req_data[0], req_data[1],
                                                        req_data[2], None, req_data[3])
