import random
from indy import ledger

from perf_load.perf_req_gen import RequestGenerator


class RGGetTxn(RequestGenerator):
    _req_types = ["3"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ledger = kwargs.get("ledger", "DOMAIN")
        self._min_seq = kwargs.get("min_seq_no", 0)
        self._max_seq = kwargs.get("max_seq_no", 10000000)
        self._rand_seq = kwargs.get("rand_seq", True)
        self._cur_seq = -1
        self._width = self._max_seq - self._min_seq

    def _rand_data(self):
        if self._rand_seq:
            self._cur_seq = random.randint(self._min_seq, self._max_seq)
        else:
            self._cur_seq = self._min_seq + ((self._cur_seq + 1) % self._width)
        return (self._ledger, int(self._cur_seq))

    async def _gen_req(self, submitter_did, req_data):
        return await ledger.build_get_txn_request(submitter_did, req_data[0], req_data[1])
