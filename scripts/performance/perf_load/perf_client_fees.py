import json
from ctypes import CDLL

from indy import payment
from indy import ledger

from perf_load.perf_client_msgs import ClientReady
from perf_load.perf_client import LoadClient
from perf_load.perf_utils import ensure_is_reply, divide_sequence_into_chunks, request_get_type


TRUSTEE_ROLE_CODE = "0"


class LoadClientFees(LoadClient):
    __initiated_plugins = set()

    @classmethod
    def __init_plugin_once(cls, plugin_lib_name, init_func_name):
        if (plugin_lib_name, init_func_name) not in cls.__initiated_plugins:
            try:
                plugin_lib = CDLL(plugin_lib_name)
                init_func = getattr(plugin_lib, init_func_name)
                res = init_func()
                if res != 0:
                    raise RuntimeError(
                        "Initialization function returned result code {}".format(res))
                cls.__initiated_plugins.add((plugin_lib_name, init_func_name))
            except Exception as ex:
                print("Payment plugin initialization failed: {}".format(repr(ex)))
                raise ex

    def __init__(self, name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **kwargs):
        super().__init__(name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **kwargs)
        self._trustee_dids = []
        self._pool_fees = {}
        self._addr_txos = {}
        self._payment_addrs_count = kwargs.get("payment_addrs_count", 100)
        self._addr_mint_limit = kwargs.get("addr_mint_limit", 1000)
        self._payment_method = kwargs.get("payment_method", "")
        self._plugin_lib = kwargs.get("plugin_lib", "")
        self._plugin_init = kwargs.get("plugin_init", "")
        self._req_num_of_trustees = kwargs.get("trustees_num", 4)
        self._set_fees = kwargs.get("set_fees", {})

        if not self._payment_method or not self._plugin_lib or not self._plugin_init:
            raise RuntimeError("Plugin cannot be initialized. Some required param missed")

    async def _add_fees(self, wallet_h, did, req):
        req_type = request_get_type(req)
        fees_val = self._pool_fees.get(req_type, 0)
        if fees_val == 0:
            return req

        for ap in self._addr_txos:
            while self._addr_txos[ap]:
                (source, amount) = self._addr_txos[ap].pop()
                if amount >= fees_val:
                    address = ap
                    inputs = [source]
                    out_val = amount - fees_val
                    outputs = []
                    if out_val > 0:
                        outputs = [{"recipient": address, "amount": out_val}]
                    req_fees = await payment.add_request_fees(wallet_h, did, req, json.dumps(inputs),
                                                              json.dumps(outputs), None)
                    return req_fees[0]
        return req

    async def ledger_sign_req(self, wallet_h, did, req):
        fees_req = await self._add_fees(wallet_h, did, req)
        return await ledger.sign_request(wallet_h, did, fees_req)

    async def _parse_fees_resp(self, resp_or_exp):
        if isinstance(resp_or_exp, Exception):
            return

        resp = resp_or_exp
        try:
            resp_obj = json.loads(resp)
            op_f = resp_obj.get("op", "")
            if op_f == "REPLY":
                receipt_infos_json = await payment.parse_response_with_fees(self._payment_method, resp)
                receipt_infos = json.loads(receipt_infos_json)
                for ri in receipt_infos:
                    self._addr_txos[ri["recipient"]].append((ri["receipt"], ri["amount"]))
            else:
                print("fees resp cannot be parsed")
        except Exception as e:
            print("Error on payment txn postprocessing: {}".format(e))

    async def ledger_submit(self, pool_h, req):
        try:
            resp = await ledger.submit_request(pool_h, req)
        except Exception as ex:
            resp = ex
        await self._parse_fees_resp(resp)
        return resp

    async def __is_trustee(self, checking_did):
        get_nym_req = await ledger.build_get_nym_request(checking_did, checking_did)
        get_nym_resp = await ledger.sign_and_submit_request(
            self._pool_handle, self._wallet_handle, checking_did, get_nym_req)
        get_nym_resp_obj = json.loads(get_nym_resp)
        ensure_is_reply(get_nym_resp_obj)
        data_f = get_nym_resp_obj["result"].get("data", None)
        if data_f is None:
            return None
        res_data = json.loads(data_f)
        if res_data["role"] != TRUSTEE_ROLE_CODE:
            return False
        return True

    async def __create_payment_addresses(self, addrs_cnt):
        ret_addrs = []
        for i in range(addrs_cnt):
            ret_addrs.append(await payment.create_payment_address(self._wallet_handle, self._payment_method, "{}"))
        return ret_addrs

    async def multisig_req(self, req):
        ret_req = req
        for d in self._trustee_dids:
            ret_req = await ledger.multi_sign_request(self._wallet_handle, d, ret_req)
        return ret_req

    async def __mint_sources(self, payment_addresses, amount):
        outputs = []
        for payment_address in payment_addresses:
            outputs.append({"recipient": payment_address, "amount": amount})

        mint_req, _ = await payment.build_mint_req(self._wallet_handle, self._test_did, json.dumps(outputs), None)
        mint_req = await self.multisig_req(mint_req)
        mint_resp = await ledger.submit_request(self._pool_handle, mint_req)
        ensure_is_reply(mint_resp)

    async def _get_payment_sources(self, pmnt_addr):
        get_ps_req, _ = await payment.build_get_payment_sources_request(self._wallet_handle, self._test_did, pmnt_addr)
        get_ps_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, get_ps_req)
        ensure_is_reply(get_ps_resp)

        source_infos_json = await payment.parse_get_payment_sources_response(self._payment_method, get_ps_resp)
        source_infos = json.loads(source_infos_json)
        payment_sources = []
        for source_info in source_infos:
            payment_sources.append((source_info["source"], source_info["amount"]))
        return {pmnt_addr: payment_sources}

    async def _did_init(self, seed):
        if len(set(seed)) != self._req_num_of_trustees:
            raise RuntimeError("Number of trustee seeds must be eq to {}".format(self._req_num_of_trustees))
        if len(set(seed)) != len(seed):
            raise RuntimeError("Duplicated seeds not allowed")

        for s in seed:
            self._test_did, self._test_verk = await self.did_create_my_did(
                self._wallet_handle, json.dumps({'seed': s}))
            is_trustee = await self.__is_trustee(self._test_did)
            if is_trustee is False:
                raise Exception("Submitter role must be TRUSTEE since "
                                "submitter have to create additional trustees to mint sources.")
            if is_trustee is None:
                assert len(self._trustee_dids) >= 1
                nym_req = await ledger.build_nym_request(self._trustee_dids[0], self._test_did, self._test_verk, None,
                                                         "TRUSTEE")
                nym_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle,
                                                                self._trustee_dids[0], nym_req)
                ensure_is_reply(nym_resp)
            self._trustee_dids.append(self._test_did)

    async def _pool_fees_init(self):
        if self._set_fees:
            fees_req = await payment.build_set_txn_fees_req(
                self._wallet_handle, self._test_did, self._payment_method, json.dumps(self._set_fees))
            fees_req = await self.multisig_req(fees_req)
            fees_resp = await ledger.submit_request(self._pool_handle, fees_req)
            ensure_is_reply(fees_resp)

        get_fees_req = await payment.build_get_txn_fees_req(self._wallet_handle, self._test_did, self._payment_method)
        get_fees_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did,
                                                             get_fees_req)
        self._pool_fees = json.loads(await payment.parse_get_txn_fees_response(self._payment_method, get_fees_resp))

    async def _payment_address_init(self):
        pmt_addrs = await self.__create_payment_addresses(self._payment_addrs_count)
        for payment_addrs_chunk in divide_sequence_into_chunks(pmt_addrs, 500):
            await self.__mint_sources(payment_addrs_chunk, self._addr_mint_limit)
        for pa in pmt_addrs:
            self._addr_txos.update(await self._get_payment_sources(pa))

    async def _pre_init(self):
        self.__init_plugin_once(self._plugin_lib, self._plugin_init)

    async def _post_init(self):
        await self._pool_fees_init()
        await self._payment_address_init()
