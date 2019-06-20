import json
import time


class ClientStatistic:
    def __init__(self, short_stat=False):
        self._short_stat = short_stat
        self._req_prep = 0
        self._req_sent = 0
        self._req_succ = 0
        self._req_fail = 0
        self._req_nack = 0
        self._req_rejc = 0

        self._client_stat_reqs = dict()

    def sent_count(self):
        return self._req_sent

    def preparing(self, req_data, test_label: str = ""):
        req_data_repr = repr(req_data)
        self._client_stat_reqs.setdefault(req_data_repr, dict())["client_preparing"] = time.time()
        self._client_stat_reqs[req_data_repr]["label"] = test_label

    def prepared(self, req_data):
        self._client_stat_reqs.setdefault(repr(req_data), dict())["client_prepared"] = time.time()

    def signed(self, req_data):
        self._client_stat_reqs.setdefault(repr(req_data), dict())["client_signed"] = time.time()
        self._req_prep += 1

    def sent(self, req_data, req):
        req_data_repr = repr(req_data)
        self._client_stat_reqs.setdefault(req_data_repr, dict())["client_sent"] = time.time()
        self._req_sent += 1
        if not self._short_stat:
            self._client_stat_reqs[req_data_repr]["req"] = req

    def reply(self, req_data, reply_or_exception):
        req_data_repr = repr(req_data)
        self._client_stat_reqs.setdefault(req_data_repr, dict())["client_reply"] = time.time()
        resp = reply_or_exception
        if isinstance(reply_or_exception, str):
            try:
                resp = json.loads(reply_or_exception)
            except Exception as e:
                resp = e

        if isinstance(resp, Exception):
            self._req_fail += 1
            status = "fail"
        elif isinstance(resp, dict) and "op" in resp:
            if resp["op"] == "REQNACK":
                self._req_nack += 1
                status = "nack"
            elif resp["op"] == "REJECT":
                self._req_rejc += 1
                status = "reject"
            elif resp["op"] == "REPLY":
                self._req_succ += 1
                status = "succ"
                srv_tm = \
                    resp['result'].get('txnTime', False) or resp['result'].get('txnMetadata', {}).get('txnTime', False)
                server_time = int(srv_tm)
                self._client_stat_reqs[req_data_repr]["server_reply"] = server_time
            else:
                self._req_fail += 1
                status = "fail"
            resp = json.dumps(resp)
        else:
            self._req_fail += 1
            status = "fail"
        self._client_stat_reqs[req_data_repr]["status"] = status
        if not self._short_stat:
            self._client_stat_reqs[req_data_repr]["resp"] = resp

    def dump_stat(self, dump_all: bool = False):
        ret_val = {}
        ret_val["total_prepared"] = self._req_prep
        ret_val["total_sent"] = self._req_sent
        ret_val["total_fail"] = self._req_fail
        ret_val["total_succ"] = self._req_succ
        ret_val["total_nacked"] = self._req_nack
        ret_val["total_rejected"] = self._req_rejc
        ret_val["reqs"] = []
        reqs = [k for k, v in self._client_stat_reqs.items() if "status" in v or dump_all]
        for r in reqs:
            ret_val["reqs"].append((r, self._client_stat_reqs.pop(r)))
        return ret_val
