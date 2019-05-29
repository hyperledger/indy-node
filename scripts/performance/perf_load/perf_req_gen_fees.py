from indy.payment import build_get_txn_fees_req

from perf_load.perf_req_gen import RequestGenerator


class RGGetFees(RequestGenerator):
    _req_types = ['20001']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._wallet_handle = None

    async def on_pool_create(self, _pool_handle, wallet_handle, _submitter_did, _sign_req_f, _send_req_f, *args, **kwargs):
        self._wallet_handle = wallet_handle

    async def _gen_req(self, submitter_did, _req_data):
        return await build_get_txn_fees_req(self._wallet_handle, submitter_did, "sov")
