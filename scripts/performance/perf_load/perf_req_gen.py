import logging
from abc import ABCMeta, abstractmethod
import json
import random

from indy import ledger
from perf_load.perf_clientstaistic import ClientStatistic
from perf_load.perf_utils import check_fs, random_string, get_type_field


class NoReqDataAvailableException(Exception):
    pass


class RequestGenerator(metaclass=ABCMeta):
    _req_types = []

    def __init__(self, label: str = "",
                 file_name: str = None, ignore_first_line: bool = True,
                 file_sep: str = "|", file_max_split: int = 2, file_field: int = 2,
                 client_stat: ClientStatistic = None, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._test_label = label
        self._client_stat = client_stat
        if not isinstance(self._client_stat, ClientStatistic):
            raise RuntimeError("Bad Statistic obj")
        random.seed()
        self._data_file = None
        self._file_start_pos = 0
        self._file_sep = file_sep if file_sep else "|"
        self._file_max_split = file_max_split
        self._file_field = file_field
        if file_name is not None:
            self._data_file = open(check_fs(is_dir=False, fs_name=file_name), "rt")
            if ignore_first_line:
                self._data_file.readline()
                self._file_start_pos = self._data_file.tell()
        self._taa_text = None
        self._taa_version = None
        self._taa_mechanism = None
        self._taa_time = None

    def get_label(self):
        return self._test_label

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        self._taa_text = kwargs.get("taa_text", "")
        self._taa_version = kwargs.get("taa_version", "")
        self._taa_mechanism = kwargs.get("taa_mechanism", "")
        self._taa_time = kwargs.get("taa_time", 0)

    def _rand_data(self):
        return random_string(32)

    def _from_file_str_data(self, file_str):
        line_vals = file_str.split(self._file_sep, maxsplit=self._file_max_split)
        if self._file_field < len(line_vals):
            tmp = json.loads(line_vals[self._file_field])
            if self._req_types and (get_type_field(tmp) in self._req_types):
                return tmp
        return None

    def _gen_req_data(self):
        if self._data_file is not None:
            while True:
                file_str = self._data_file.readline()
                if not file_str:
                    self._data_file.seek(self._file_start_pos)
                    file_str = self._data_file.readline()
                    if not file_str:
                        raise RuntimeError("Data file does not contain valid entries")
                tmp = self._from_file_str_data(file_str)
                if tmp is not None:
                    return tmp
        else:
            return self._rand_data()

    async def _append_taa_acceptance(self, req):
        if self._taa_text == "":
            return req

        return await ledger.append_txn_author_agreement_acceptance_to_request(
            req, self._taa_text, self._taa_version, None, self._taa_mechanism, self._taa_time)

    @abstractmethod
    async def _gen_req(self, submit_did, req_data):
        pass

    async def generate_request(self, submit_did):
        req_data = self._gen_req_data()
        self._client_stat.preparing(req_data, self.get_label())

        try:
            req = await self._gen_req(submit_did, req_data)
            self._client_stat.prepared(req_data)
        except Exception as ex:
            self._client_stat.reply(req_data, ex)
            raise ex

        return req_data, req

    async def on_request_generated(self, req_data, gen_req):
        pass

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        pass

    def req_did(self):
        return None
