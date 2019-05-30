import json
import random

from indy import payment
from indy import ledger

from perf_load.perf_utils import ensure_is_reply, gen_input_output, PUB_XFER_TXN_ID, log_addr_txos_update
from perf_load.perf_req_gen import NoReqDataAvailableException, RequestGenerator


class RGBasePayment(RequestGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pool_handle = None
        self._wallet_handle = None
        self._submitter_did = None
        self._payment_method = None
        self._addr_txos = None
        self._payment_fees = 0

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        self._pool_handle = pool_handle
        self._wallet_handle = wallet_handle
        self._submitter_did = submitter_did
        self._payment_method = kwargs.get("payment_method", "")
        self._addr_txos = kwargs.get("addr_txos", {})
        self._payment_fees = kwargs.get("pool_fees", {}).get(PUB_XFER_TXN_ID, 0)

        if not self._payment_method or not self._addr_txos:
            raise RuntimeError("Payment init incorrect parameters")

    def _gen_input_output(self, val, fees):
        address, inputs, outputs = gen_input_output(self._addr_txos, val + fees)
        if inputs is None or outputs is None:
            self._logger.warning("Failed to create XFER, insufficient txos")
            raise NoReqDataAvailableException()
        log_addr_txos_update('XFER', self._addr_txos, -len(inputs))

        addrs = list(self._addr_txos)
        addrs.remove(list(address)[0])
        to_address = random.choice(addrs)
        outputs.append({"recipient": to_address, "amount": val})

        return inputs, outputs


class RGGetPaymentSources(RGBasePayment):
    def _gen_req_data(self):
        return random.choice(list(self._addr_txos))

    async def _gen_req(self, submit_did, req_data):
        req, _ = await payment.build_get_payment_sources_request(self._wallet_handle, self._submitter_did, req_data)
        return req


class RGPayment(RGBasePayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sent_reqs = set()

    def _gen_req_data(self):
        return self._gen_input_output(1, self._payment_fees)

    async def _gen_req(self, submit_did, req_data):
        inputs, outputs = req_data
        extra = None
        if self._taa_text:
            extra = await payment.prepare_payment_extra_with_acceptance_data(
                None, self._taa_text, self._taa_version, None, self._taa_mechanism, self._taa_time)
        req, _ = await payment.build_payment_req(
            self._wallet_handle, self._submitter_did, json.dumps(inputs), json.dumps(outputs), extra)
        return req

    async def on_request_generated(self, req_data, gen_req):
        self._sent_reqs.add(gen_req)

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        if gen_req not in self._sent_reqs:
            return

        self._sent_reqs.remove(gen_req)

        if isinstance(resp_or_exp, Exception):
            return

        reply = json.loads(resp_or_exp)
        result = reply.get('result')
        if not result or result['txn']['type'] != PUB_XFER_TXN_ID:
            return

        try:
            receipt_infos_json = await payment.parse_payment_response(self._payment_method, resp_or_exp)
            receipt_infos = json.loads(receipt_infos_json) if receipt_infos_json else []
            for ri in receipt_infos:
                self._addr_txos[ri["recipient"]].append((ri["receipt"], ri["amount"]))
            log_addr_txos_update('XFER', self._addr_txos, len(receipt_infos))
        except Exception as e:
            self._logger.info('Got unexpected error: {}'.format(e))
            self._logger.info('While parsing reply: {}'.format(reply))
            raise


class RGVerifyPayment(RGBasePayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._receipts = []

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        await self.__perform_payments()

    async def __perform_payments(self):
        for i in range(len(self._addr_txos)):
            try:
                inputs, outputs = self._gen_input_output(1, self._payment_fees)
            except NoReqDataAvailableException:
                break

            extra = None
            if self._taa_text:
                extra = await payment.prepare_payment_extra_with_acceptance_data(
                    None, self._taa_text, self._taa_version, None, self._taa_mechanism, self._taa_time)
            req, _ = await payment.build_payment_req(
                self._wallet_handle, self._submitter_did, json.dumps(inputs), json.dumps(outputs), extra)

            resp = await ledger.sign_and_submit_request(
                self._pool_handle, self._wallet_handle, self._submitter_did, req)
            ensure_is_reply(resp)

            try:
                receipt_infos_json = await payment.parse_payment_response(self._payment_method, resp)
                receipt_infos = json.loads(receipt_infos_json) if receipt_infos_json else []
                for receipt_info in receipt_infos:
                    self._receipts.append(receipt_info["receipt"])
            except Exception:
                pass

    def _gen_req_data(self):
        if not self._receipts:
            raise NoReqDataAvailableException()
        return random.choice(self._receipts)

    async def _gen_req(self, submit_did, req_data):
        receipt = req_data
        req, _ = await payment.build_verify_payment_req(self._wallet_handle, self._submitter_did, receipt)
        return req
