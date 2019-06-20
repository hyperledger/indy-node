import json
import random
import string
from ctypes import CDLL

from indy import payment
from indy import ledger

from perf_load.perf_client import LoadClient
from perf_load.perf_utils import ensure_is_reply, divide_sequence_into_chunks, \
    request_get_type, gen_input_output, PUB_XFER_TXN_ID, response_get_type, log_addr_txos_update


class LoadClientFees(LoadClient):
    __initiated_plugins = set()
    __pool_fees = []
    __auth_rule_metadata = []

    FEES_ALIAS_PREFIX = "_fees_alias_prefix"

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

    @classmethod
    async def __set_fees_once(cls, wallet_handle, set_fees, test_did, payment_method, trustee_dids, pool_handle):
        if not len(cls.__pool_fees):
            if set_fees:
                fees_req = await payment.build_set_txn_fees_req(
                    wallet_handle, test_did, payment_method, json.dumps(set_fees))
                for d in trustee_dids:
                    fees_req = await ledger.multi_sign_request(wallet_handle, d, fees_req)
                fees_resp = await ledger.submit_request(pool_handle, fees_req)
                ensure_is_reply(fees_resp)

            get_fees_req = await payment.build_get_txn_fees_req(wallet_handle, test_did, payment_method)
            get_fees_resp = await ledger.sign_and_submit_request(pool_handle, wallet_handle, test_did, get_fees_req)

            fees_set = json.loads(await payment.parse_get_txn_fees_response(payment_method, get_fees_resp))
            cls.__pool_fees = {cls._get_txn_type_by_alis(alias): fees_amount for alias, fees_amount in fees_set.items()}

        return cls.__pool_fees

    def __init__(self, name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, short_stat,
                 **kwargs):
        super().__init__(name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode,
                         short_stat, **kwargs)
        self._pool_fees = {}
        self._ignore_fees_txns = [PUB_XFER_TXN_ID]
        self._addr_txos = {}
        self._payment_addrs_count = kwargs.get("payment_addrs_count", 100)
        self._mint_addrs_count = kwargs.get("mint_addrs_count", self._payment_addrs_count)
        self._addr_mint_limit = kwargs.get("addr_mint_limit", 1000)
        self._payment_method = kwargs.get("payment_method", "")
        self._plugin_lib = kwargs.get("plugin_lib", "")
        self._plugin_init = kwargs.get("plugin_init", "")
        self._req_num_of_trustees = kwargs.get("trustees_num", 4)
        self._init_fees_params(kwargs.get("set_fees", {}))
        self._allow_invalid_txns = kwargs.get("allow_invalid_txns", 0)
        self._req_addrs = {}
        self._mint_by = kwargs.get("mint_by", self._addr_mint_limit)
        if self._mint_by < 1 or self._mint_by > self._addr_mint_limit:
            self._mint_by = self._addr_mint_limit
        self._mint_addrs_count = min(self._mint_addrs_count, self._payment_addrs_count)

        if not self._payment_method or not self._plugin_lib or not self._plugin_init:
            raise RuntimeError("Plugin cannot be initialized. Some required param missed")

    def _init_fees_params(self, set_fees_param):
        # txn_type -> {fees: alias} metadata
        self._auth_rule_metadata = {txn_type: {"fees": self._create_alias(txn_type)} for txn_type, _ in
                                    set_fees_param.items()}

        # alias -> amount
        self._set_fees = {self._create_alias(txn_type): fees_amount for txn_type, fees_amount in set_fees_param.items()}

    @staticmethod
    def _create_alias(txn_type):
        return txn_type + LoadClientFees.FEES_ALIAS_PREFIX

    @staticmethod
    def _get_txn_type_by_alis(alias):
        return alias[:-len(LoadClientFees.FEES_ALIAS_PREFIX)]

    async def _add_fees(self, wallet_h, did, req):
        req_type = request_get_type(req)

        if req_type in self._ignore_fees_txns:
            return None, req

        fees_val = self._pool_fees.get(req_type, 0)
        if fees_val == 0:
            return None, req

        address, inputs, outputs = gen_input_output(self._addr_txos, fees_val)
        if not inputs:
            self._logger.warning("Failed to add fees to txn, insufficient txos")
            return None, req if self._allow_invalid_txns else None

        log_addr_txos_update('FEES', self._addr_txos, -len(inputs))
        req_fees, _ = await payment.add_request_fees(wallet_h, did, req, json.dumps(inputs),
                                                     json.dumps(outputs), None)
        return address, req_fees

    async def ledger_sign_req(self, wallet_h, did, req):
        addr, fees_req = await self._add_fees(wallet_h, did, req)
        if fees_req is None:
            return None
        req = await ledger.sign_request(wallet_h, did, fees_req)
        if addr is not None:
            self._req_addrs[req] = addr
        return req

    def _restore_fees_from_req(self, req):
        fees_to_restore = self._req_addrs.pop(req, {})
        for addr, txos in fees_to_restore.items():
            self._addr_txos[addr].extend(txos)
            log_addr_txos_update('RESTORE', self._addr_txos, len(txos))

    async def _parse_fees_resp(self, req, resp_or_exp):
        if isinstance(resp_or_exp, Exception):
            self._logger.warning("Pool responded with error, UTXOs are lost: {}".format(self._req_addrs.get(req)))
            self._req_addrs.pop(req, {})
            return

        resp = resp_or_exp
        try:
            resp_obj = json.loads(resp)
            op_f = resp_obj.get("op", "")
            resp_type = response_get_type(resp_obj)
            if op_f == "REPLY" and resp_type not in self._ignore_fees_txns:
                receipt_infos_json = await payment.parse_response_with_fees(self._payment_method, resp)
                receipt_infos = json.loads(receipt_infos_json) if receipt_infos_json else []
                for ri in receipt_infos:
                    self._addr_txos[ri["recipient"]].append((ri["receipt"], ri["amount"]))
                log_addr_txos_update('FEES', self._addr_txos, len(receipt_infos))
            else:
                self._restore_fees_from_req(req)
        except Exception as e:
            self._logger.exception("Error on payment txn postprocessing: {}".format(e))
        self._req_addrs.pop(req, {})

    async def ledger_submit(self, pool_h, req):
        try:
            resp = await ledger.submit_request(pool_h, req)
        except Exception as ex:
            resp = ex
        await self._parse_fees_resp(req, resp)
        return resp

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

    async def __mint_sources(self, payment_addresses, amount, by_val):
        iters = (amount // by_val) + (1 if (amount % by_val) > 0 else 0)
        mint_val = by_val
        for i in range(iters):
            outputs = []
            if (i + 1) * by_val > amount:
                mint_val = amount % by_val
            for payment_address in payment_addresses:
                outputs.append({"recipient": payment_address, "amount": mint_val})
            mint_req, _ = await payment.build_mint_req(self._wallet_handle, self._test_did, json.dumps(outputs), None)
            mint_req = await self.append_taa_acceptance(mint_req)
            mint_req = await self.multisig_req(mint_req)
            mint_resp = await ledger.submit_request(self._pool_handle, mint_req)
            ensure_is_reply(mint_resp)

    async def _get_payment_sources(self, pmnt_addr):
        get_ps_req, _ = await payment.build_get_payment_sources_request(self._wallet_handle, self._test_did, pmnt_addr)
        get_ps_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did,
                                                           get_ps_req)
        ensure_is_reply(get_ps_resp)

        source_infos_json = await payment.parse_get_payment_sources_response(self._payment_method, get_ps_resp)
        source_infos = json.loads(source_infos_json)
        payment_sources = []
        for source_info in source_infos:
            payment_sources.append((source_info["source"], source_info["amount"]))
        return {pmnt_addr: payment_sources}

    async def _pool_fees_init(self):
        # _pool_fees: txn_type -> amount
        # _auth_rule_metadata: txn_type -> {fees: alias} metadata
        self._pool_fees = await self.__set_fees_once(self._wallet_handle, self._set_fees,
                                                     self._test_did, self._payment_method,
                                                     self._trustee_dids, self._pool_handle)
        self._logger.info("_pool_fees_init done")

    async def _payment_address_init(self):
        pmt_addrs = await self.__create_payment_addresses(self._payment_addrs_count)
        mint_addrs = pmt_addrs[:self._mint_addrs_count]
        for payment_addrs_chunk in divide_sequence_into_chunks(mint_addrs, 500):
            await self.__mint_sources(payment_addrs_chunk, self._addr_mint_limit, self._mint_by)
        for pa in pmt_addrs:
            self._addr_txos.update(await self._get_payment_sources(pa))
        log_addr_txos_update('MINT', self._addr_txos)
        self._logger.info("_payment_address_init done")

    async def _pre_init(self):
        self.__init_plugin_once(self._plugin_lib, self._plugin_init)
        self._logger.info("_pre_init done")

    async def _post_init(self):
        await self._pool_fees_init()
        await self._payment_address_init()
        await super()._post_init()  # Actually this is just a call to self._pool_auth_rules_init()
        self._logger.info("_post_init done")

    def _on_pool_create_ext_params(self):
        params = super()._on_pool_create_ext_params()
        params.update({"addr_txos": self._addr_txos,
                       "payment_method": self._payment_method,
                       "pool_fees": self._pool_fees})
        self._logger.info("_on_pool_create_ext_params done {}".format(params))
        return params


def random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))
