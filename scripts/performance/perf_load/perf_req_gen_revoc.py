import json
import time
import libnacl
import random

from indy import ledger, anoncreds, blob_storage

from perf_load.perf_utils import rawToFriendly, random_string, get_txnid_field
from perf_load.perf_req_gen_definition import RGDefinition
from perf_load.perf_req_gen import NoReqDataAvailableException


class RGDefRevoc(RGDefinition):
    _req_types = ["113", "115"]

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        dr = await ledger.build_cred_def_request(submitter_did, json.dumps(self._default_definition_json))
        dr = await self._append_taa_acceptance(dr)
        resp = await sign_req_f(wallet_handle, submitter_did, dr)
        await send_req_f(pool_handle, resp)

    async def _gen_req(self, submit_did, req_data):
        tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
        tails_writer = await blob_storage.open_writer('default', tails_writer_config)
        _, revoc_reg_def_json, revoc_reg_entry_json = await anoncreds.issuer_create_and_store_revoc_reg(
            self._wallet_handle, submit_did, "CL_ACCUM", req_data, self._default_definition_id,
            json.dumps({"max_cred_num": 5, "issuance_type": "ISSUANCE_BY_DEFAULT"}), tails_writer)
        return await ledger.build_revoc_reg_def_request(submit_did, revoc_reg_def_json)

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        return get_txnid_field(req_json)


class RGGetDefRevoc(RGDefRevoc):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        submitter_did = rawToFriendly(raw)
        cred_def_id = ':'.join([submitter_did, '3', 'CL', '1'])
        def_revoc_id = ':'.join([submitter_did, '4', cred_def_id, 'CL_ACCUM', 'reg1'])
        return def_revoc_id

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        pass

    async def on_request_generated(self, req_data, gen_req):
        pass

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        pass

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_revoc_reg_def_request(submit_did, req_data)
        return req


class RGEntryRevoc(RGDefRevoc):
    _req_types = ["114", "116", "117"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_revoc_reg_def_id = None
        self._default_revoc_reg_def_json = None
        self._default_revoc_reg_entry_json = None
        self._blob_storage_reader_cfg_handle = None
        self._default_cred_values_json = json.dumps({
            "name": {"raw": "value1", "encoded": "123"},
            "age": {"raw": "value1", "encoded": "456"},
            "sex": {"raw": "value1", "encoded": "123"},
            "height": {"raw": "value1", "encoded": "456"}
        })
        self._max_cred_num = None
        self._submitter_did = None
        self._pool_handle = None
        self._cred_offer_json = None
        self._tails_writer = None
        self._master_secret_id = None

        self._old_reqs = set()
        self._old_reqs_cnt = 0

        self._sign_req = None
        self._submit_req = None

    async def _upd_revoc_reg(self):
        while True:
            try:
                self._default_revoc_reg_def_id, self._default_revoc_reg_def_json, self._default_revoc_reg_entry_json = \
                    await anoncreds.issuer_create_and_store_revoc_reg(
                        self._wallet_handle, self._submitter_did, "CL_ACCUM", random_string(32),
                        self._default_definition_id,
                        json.dumps({"max_cred_num": self._max_cred_num, "issuance_type": "ISSUANCE_ON_DEMAND"}),
                        self._tails_writer)
                def_revoc_request = await ledger.build_revoc_reg_def_request(
                    self._submitter_did, self._default_revoc_reg_def_json)
                def_revoc_request = await self._append_taa_acceptance(def_revoc_request)
                def_revoc_request = await self._sign_req(self._wallet_handle, self._submitter_did, def_revoc_request)
                await self._submit_req(self._pool_handle, def_revoc_request)
                entry_revoc_request = await ledger.build_revoc_reg_entry_request(
                    self._submitter_did, self._default_revoc_reg_def_id, "CL_ACCUM", self._default_revoc_reg_entry_json)
                entry_revoc_request = await self._append_taa_acceptance(entry_revoc_request)
                entry_revoc_request = await self._sign_req(self._wallet_handle, self._submitter_did, entry_revoc_request)
                await self._submit_req(self._pool_handle, entry_revoc_request)
                break
            except Exception as ex:
                print("WARNING: _upd_revoc_reg {}".format(ex))

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        self._sign_req = sign_req_f
        self._submit_req = send_req_f
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        self._max_cred_num = kwargs["max_cred_num"] if "max_cred_num" in kwargs else 100
        self._wallet_handle = wallet_handle
        self._submitter_did = submitter_did
        self._pool_handle = pool_handle
        self._cred_offer_json = await anoncreds.issuer_create_credential_offer(
            self._wallet_handle, self._default_definition_id)
        self._master_secret_id = await anoncreds.prover_create_master_secret(
            self._wallet_handle, master_secret_name='')
        tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
        self._tails_writer = await blob_storage.open_writer('default', tails_writer_config)
        self._blob_storage_reader_cfg_handle = await blob_storage.open_reader('default', tails_writer_config)
        await self._upd_revoc_reg()

    async def _gen_req(self, submit_did, req_data):
        cred_req_json, _ = await anoncreds.prover_create_credential_req(
            self._wallet_handle, submit_did, self._cred_offer_json,
            json.dumps(self._default_definition_json), self._master_secret_id)
        _, _, revoc_reg_delta_json = await anoncreds.issuer_create_credential(
            self._wallet_handle, self._cred_offer_json, cred_req_json, self._default_cred_values_json,
            self._default_revoc_reg_def_id, self._blob_storage_reader_cfg_handle)
        try:
            req = await ledger.build_revoc_reg_entry_request(submit_did, self._default_revoc_reg_def_id,
                                                             "CL_ACCUM", revoc_reg_delta_json)
        except Exception as ex:
            self._old_reqs_cnt = 0
            await self._upd_revoc_reg()
            raise NoReqDataAvailableException()
        return req

    def _gen_req_data(self):
        req_data = super()._gen_req_data()
        self._old_reqs.add(req_data)
        return req_data

    async def on_request_generated(self, req_data, gen_req):
        if req_data in self._old_reqs:
            self._old_reqs_cnt += 1
            self._old_reqs.remove(req_data)

        if self._old_reqs_cnt >= self._max_cred_num:
            self._old_reqs_cnt = 0
            await self._upd_revoc_reg()

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        pass

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        return get_txnid_field(req_json)


class RGGetEntryRevoc(RGEntryRevoc):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        submitter_did = rawToFriendly(raw)
        cred_def_id = ':'.join([submitter_did, '03', 'CL', str(random.randint(1, 100))])
        def_revoc_id = ':'.join([submitter_did, '04', cred_def_id, 'CL_ACCUM', 'reg1'])
        entry_revoc_id = ':'.join([submitter_did, '05', def_revoc_id])
        return entry_revoc_id

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        pass

    async def on_request_generated(self, req_data, gen_req):
        pass

    async def _gen_req(self, submit_did, req_data):
        timestamp = int(time.time())
        req = await ledger.build_get_revoc_reg_request(submit_did, req_data, timestamp)
        return req


class RGGetRevocRegDelta(RGGetEntryRevoc):
    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_revoc_reg_delta_request(submit_did, req_data, None, int(time.time()))
        return req

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        pass

    async def on_request_generated(self, req_data, gen_req):
        pass
