import json
import libnacl
from indy import payment
from indy import ledger, anoncreds

from scripts.performance.perf_utils import ensure_is_reply, rawToFriendly
from scripts.performance.perf_req_gen import NoReqDataAvailableException
from scripts.performance.perf_req_gen_payment import RGBasePayment


class RGFeesNym(RGBasePayment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sources_amounts = {}
        self._last_used = None

    async def __retrieve_minted_sources(self):
        for payment_address in self._payment_addresses:
            self._sources_amounts[payment_address] = []
            self._sources_amounts[payment_address].extend(await self._get_payment_sources(payment_address))

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, *args, **kwargs)
        await self.__retrieve_minted_sources()

        fees_req = await payment.build_set_txn_fees_req(wallet_handle, submitter_did, self._payment_method,
                                                        json.dumps({"1": 1}))
        for trustee_did in [self._submitter_did, *self._additional_trustees_dids]:
            fees_req = await ledger.multi_sign_request(self._wallet_handle, trustee_did, fees_req)

        resp = await ledger.submit_request(self._pool_handle, fees_req)
        ensure_is_reply(resp)

    def _rand_data(self):
        raw = libnacl.randombytes(16)
        req_did = rawToFriendly(raw)
        return req_did

    def _from_file_str_data(self, file_str):
        raise NotImplementedError("ne _from_file_str_data")

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_nym_request(submit_did, req_data, None, None, None)

        for ap in self._sources_amounts:
            if self._sources_amounts[ap]:
                (source, amount) = self._sources_amounts[ap].pop()
                address = ap
                inputs = [source]
                outputs = [{"recipient": address, "amount": amount - 1}]
                req_fees = await payment.add_request_fees(self._wallet_handle, submit_did, req,
                                                          json.dumps(inputs),
                                                          json.dumps(outputs), None)
                return req_fees[0]
        raise NoReqDataAvailableException()

    async def on_request_replied(self, req_data, req, resp_or_exp):
        if isinstance(resp_or_exp, Exception):
            return

        resp = resp_or_exp

        try:
            resp_obj = json.loads(resp)

            if "op" not in resp_obj:
                raise Exception("Response does not contain op field.")

            if resp_obj["op"] == "REQNACK" or resp_obj["op"] == "REJECT":
                return
                # self._sources_amounts.append((source, amount))
            elif resp_obj["op"] == "REPLY":
                receipt_infos_json = await payment.parse_response_with_fees(self._payment_method, resp)
                receipt_infos = json.loads(receipt_infos_json)
                receipt_info = receipt_infos[0]
                self._sources_amounts[receipt_info["recipient"]].append((receipt_info["receipt"], receipt_info["amount"]))

        except Exception as e:
            print("Error on payment txn postprocessing: {}".format(e))


class RGFeesSchema(RGFeesNym):
    async def _gen_req(self, submit_did, req_data):
        _, schema_json = await anoncreds.issuer_create_schema(submit_did, req_data,
                                                              "1.0", json.dumps(["name", "age", "sex", "height"]))
        schema_request = await ledger.build_schema_request(submit_did, schema_json)

        for ap in self._sources_amounts:
            if self._sources_amounts[ap]:
                (source, amount) = self._sources_amounts[ap].pop()
                address = ap
                inputs = [source]
                outputs = [{"recipient": address, "amount": amount - 1}]
                req_fees = await payment.add_request_fees(self._wallet_handle, submit_did, schema_request,
                                                          json.dumps(inputs),
                                                          json.dumps(outputs), None)
                return req_fees[0]
        raise NoReqDataAvailableException()

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, *args, **kwargs)

        fees_req = await payment.build_set_txn_fees_req(wallet_handle, submitter_did, self._payment_method,
                                                        json.dumps({"101": 1}))
        for trustee_did in [self._submitter_did, *self._additional_trustees_dids]:
            fees_req = await ledger.multi_sign_request(self._wallet_handle, trustee_did, fees_req)

        resp = await ledger.submit_request(self._pool_handle, fees_req)
        ensure_is_reply(resp)
