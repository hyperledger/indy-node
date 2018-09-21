from abc import ABCMeta
import json
from collections import deque
from ctypes import CDLL
from datetime import datetime
import random

from indy import payment
from indy import did, ledger

from perf_load.perf_utils import ensure_is_reply, divide_sequence_into_chunks
from perf_load.perf_req_gen import NoReqDataAvailableException, RequestGenerator


class RGBasePayment(RequestGenerator, metaclass=ABCMeta):
    TRUSTEE_ROLE_CODE = "0"

    DEFAULT_PAYMENT_ADDRS_COUNT = 100

    NUMBER_OF_TRUSTEES_FOR_MINT = 4
    MINT_RECIPIENTS_LIMIT = 100
    AMOUNT_LIMIT = 100

    __initiated_plugins = set()

    @staticmethod
    def __init_plugin_once(plugin_lib_name, init_func_name):
        if (plugin_lib_name, init_func_name) not in RGBasePayment.__initiated_plugins:
            try:
                plugin_lib = CDLL(plugin_lib_name)
                init_func = getattr(plugin_lib, init_func_name)
                res = init_func()
                if res != 0:
                    raise RuntimeError(
                        "Initialization function returned result code {}".format(res))
                RGBasePayment.__initiated_plugins.add((plugin_lib_name, init_func_name))
            except Exception as ex:
                print("Payment plugin initialization failed: {}".format(repr(ex)))
                raise ex

    def __init__(self, *args,
                 payment_method,
                 plugin_lib,
                 plugin_init_func,
                 payment_addrs_count=DEFAULT_PAYMENT_ADDRS_COUNT,
                 **kwargs):

        super().__init__(*args, **kwargs)

        RGBasePayment.__init_plugin_once(plugin_lib,
                                         plugin_init_func)

        self._pool_handle = None
        self._wallet_handle = None
        self._submitter_did = None

        self._payment_method = payment_method
        self._payment_addrs_count = payment_addrs_count
        self._payment_addresses = []
        self._additional_trustees_dids = []

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)

        self._pool_handle = pool_handle
        self._wallet_handle = wallet_handle
        self._submitter_did = submitter_did

        await self.__ensure_submitter_is_trustee()

        self._additional_trustees_dids = await self.__create_additional_trustees()

        await self.__create_payment_addresses()

        for payment_addrs_chunk in divide_sequence_into_chunks(self._payment_addresses,
                                                               RGBasePayment.MINT_RECIPIENTS_LIMIT):
            await self.__mint_sources(payment_addrs_chunk, [self._submitter_did, *self._additional_trustees_dids])

    async def __ensure_submitter_is_trustee(self):
        get_nym_req = await ledger.build_get_nym_request(self._submitter_did, self._submitter_did)
        get_nym_resp = await ledger.sign_and_submit_request(self._pool_handle,
                                                            self._wallet_handle,
                                                            self._submitter_did,
                                                            get_nym_req)
        get_nym_resp_obj = json.loads(get_nym_resp)
        ensure_is_reply(get_nym_resp_obj)
        res_data = json.loads(get_nym_resp_obj["result"]["data"])
        if res_data["role"] != RGBasePayment.TRUSTEE_ROLE_CODE:
            raise Exception("Submitter role must be TRUSTEE since "
                            "submitter have to create additional trustees to mint sources.")

    async def __create_additional_trustees(self):
        trustee_dids = []

        for i in range(RGBasePayment.NUMBER_OF_TRUSTEES_FOR_MINT - 1):
            tr_seed = "Trustee{}".format(2 + i)
            tr_seed = "{}{}".format(tr_seed, "0" * (32 - len(tr_seed)))
            tr_did, tr_verkey = await did.create_and_store_my_did(self._wallet_handle, json.dumps({'seed': tr_seed}))

            nym_req = await ledger.build_nym_request(self._submitter_did, tr_did, tr_verkey, None, "TRUSTEE")
            await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._submitter_did, nym_req)

            # nym_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._submitter_did, nym_req)
            # ensure_is_reply(nym_resp)

            trustee_dids.append(tr_did)

        return trustee_dids

    async def __create_payment_addresses(self):
        for i in range(self._payment_addrs_count):
            self._payment_addresses.append(
                await payment.create_payment_address(self._wallet_handle, self._payment_method, "{}"))

    async def __mint_sources(self, payment_addresses, trustees_dids):
        outputs = []
        for payment_address in payment_addresses:
            outputs.append({"recipient": payment_address, "amount": random.randint(1, RGBasePayment.AMOUNT_LIMIT)})

        mint_req, _ = await payment.build_mint_req(self._wallet_handle,
                                                   self._submitter_did,
                                                   json.dumps(outputs),
                                                   None)

        for trustee_did in trustees_dids:
            mint_req = await ledger.multi_sign_request(self._wallet_handle, trustee_did, mint_req)

        mint_resp = await ledger.submit_request(self._pool_handle, mint_req)
        ensure_is_reply(mint_resp)

    async def _get_payment_sources(self, payment_address):
        get_payment_sources_req, _ = \
            await payment.build_get_payment_sources_request(self._wallet_handle,
                                                            self._submitter_did,
                                                            payment_address)
        get_payment_sources_resp = \
            await ledger.sign_and_submit_request(self._pool_handle,
                                                 self._wallet_handle,
                                                 self._submitter_did,
                                                 get_payment_sources_req)
        ensure_is_reply(get_payment_sources_resp)

        source_infos_json = \
            await payment.parse_get_payment_sources_response(self._payment_method,
                                                             get_payment_sources_resp)
        source_infos = json.loads(source_infos_json)
        payment_sources = []
        for source_info in source_infos:
            payment_sources.append((source_info["source"], source_info["amount"]))
        return payment_sources


class RGGetPaymentSources(RGBasePayment):
    def _gen_req_data(self):
        return (datetime.now().isoformat(), random.choice(self._payment_addresses))

    async def _gen_req(self, submit_did, req_data):
        _, payment_address = req_data
        req, _ = await payment.build_get_payment_sources_request(self._wallet_handle,
                                                                 self._submitter_did,
                                                                 payment_address)
        return req


class RGPayment(RGBasePayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sources_amounts = deque()
        self.__req_id_to_source_amount = {}
        self._old_reqs = set()

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        await self.__retrieve_minted_sources()

    async def __retrieve_minted_sources(self):
        for payment_address in self._payment_addresses:
            self._sources_amounts.extend(await self._get_payment_sources(payment_address))

    def _gen_req_data(self):
        if len(self._sources_amounts) == 0:
            raise NoReqDataAvailableException()

        source, amount = self._sources_amounts.popleft()
        address = random.choice(self._payment_addresses)

        inputs = [source]
        outputs = [{"recipient": address, "amount": amount}]

        return inputs, outputs

    async def _gen_req(self, submit_did, req_data):
        inputs, outputs = req_data
        req, _ = await payment.build_payment_req(self._wallet_handle,
                                                 self._submitter_did,
                                                 json.dumps(inputs),
                                                 json.dumps(outputs),
                                                 None)

        req_obj = json.loads(req)
        req_id = req_obj["reqId"]
        source = inputs[0]
        amount = outputs[0]["amount"]
        self.__req_id_to_source_amount[req_id] = source, amount

        self._old_reqs.add(req_id)

        return req

    async def on_request_replied(self, req_data, req, resp_or_exp):
        req_obj = json.loads(req)
        req_id = req_obj.get("reqId", None)
        if req_id not in self._old_reqs:
            return
        self._old_reqs.remove(req_id)

        if isinstance(resp_or_exp, Exception):
            return

        resp = resp_or_exp

        try:
            source, amount = self.__req_id_to_source_amount.pop(req_id)

            resp_obj = json.loads(resp)

            if "op" not in resp_obj:
                raise Exception("Response does not contain op field.")

            if resp_obj["op"] == "REQNACK" or resp_obj["op"] == "REJECT":
                self._sources_amounts.append((source, amount))
            elif resp_obj["op"] == "REPLY":
                receipt_infos_json = await payment.parse_payment_response(self._payment_method, resp)
                receipt_infos = json.loads(receipt_infos_json)
                receipt_info = receipt_infos[0]
                self._sources_amounts.append((receipt_info["receipt"], receipt_info["amount"]))

        except Exception as e:
            print("Error on payment txn postprocessing: {}".format(e))


class RGVerifyPayment(RGBasePayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sources_amounts = []
        self._receipts = []

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        await self.__retrieve_minted_sources()
        await self.__perform_payments()

    async def __retrieve_minted_sources(self):
        for payment_address in self._payment_addresses:
            self._sources_amounts.extend(await self._get_payment_sources(payment_address))

    async def __perform_payments(self):
        for source, amount in self._sources_amounts:
            address = random.choice(self._payment_addresses)

            inputs = [source]
            outputs = [{"recipient": address, "amount": amount}]

            payment_req, _ = await payment.build_payment_req(self._wallet_handle,
                                                             self._submitter_did,
                                                             json.dumps(inputs),
                                                             json.dumps(outputs),
                                                             None)

            payment_resp = await ledger.sign_and_submit_request(self._pool_handle,
                                                                self._wallet_handle,
                                                                self._submitter_did,
                                                                payment_req)
            ensure_is_reply(payment_resp)

            receipt_infos_json = await payment.parse_payment_response(self._payment_method, payment_resp)
            receipt_infos = json.loads(receipt_infos_json)
            receipt_info = receipt_infos[0]

            self._receipts.append(receipt_info["receipt"])

    def _gen_req_data(self):
        return (datetime.now().isoformat(), random.choice(self._receipts))

    async def _gen_req(self, submit_did, req_data):
        _, receipt = req_data
        req, _ = await payment.build_verify_payment_req(self._wallet_handle,
                                                        self._submitter_did,
                                                        receipt)
        return req
