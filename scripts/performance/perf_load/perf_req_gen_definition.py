import json
from indy import ledger, anoncreds

from perf_load.perf_utils import random_string, get_txnid_field
from perf_load.perf_req_gen import RequestGenerator


class RGGetDefinition(RequestGenerator):
    _req_types = ["102", "108"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._submitter_did = None

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        self._submitter_did = submitter_did

    def _make_cred_def_id(self, shcema_id, tag):
        cred_def_marker = '03'
        signature_type = 'CL'
        cred_def_id = ':'.join([self._submitter_did, cred_def_marker, signature_type, str(shcema_id), tag])
        return cred_def_id

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        return get_txnid_field(req_json)

    async def _gen_req(self, submit_did, req_data):
        if self._data_file is not None:
            dt = req_data
        else:
            dt = self._make_cred_def_id('1', req_data)
        return await ledger.build_get_cred_def_request(submit_did, dt)


class RGDefinition(RGGetDefinition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._wallet_handle = None
        self._default_schema_json = None
        self._default_definition_id = None
        self._default_definition_json = None

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, sign_req_f, send_req_f, *args, **kwargs)
        self._wallet_handle = wallet_handle
        _, self._default_schema_json = await anoncreds.issuer_create_schema(
            submitter_did, random_string(32), "1.0", json.dumps(["name", "age", "sex", "height"]))
        schema_request = await ledger.build_schema_request(submitter_did, self._default_schema_json)
        schema_request = await self._append_taa_acceptance(schema_request)
        resp = await sign_req_f(wallet_handle, submitter_did, schema_request)
        resp = await send_req_f(pool_handle, resp)
        # resp = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, schema_request)
        resp = json.loads(resp)
        seqno =\
            resp.get('result', {}).get('seqNo', None) or\
            resp.get('result', {}).get('txnMetadata', {}).get('seqNo', None)
        self._default_schema_json = json.loads(self._default_schema_json)
        self._default_schema_json['seqNo'] = seqno
        self._default_definition_id, self._default_definition_json = \
            await anoncreds.issuer_create_and_store_credential_def(
                wallet_handle, submitter_did, json.dumps(self._default_schema_json),
                random_string(32), "CL", json.dumps({"support_revocation": True}))
        self._default_definition_json = json.loads(self._default_definition_json)

    async def _gen_req(self, submit_did, req_data):
        if self._data_file is not None:
            dt = req_data
        else:
            self._default_definition_id = self._make_cred_def_id(self._default_schema_json['seqNo'], req_data)
            self._default_definition_json["id"] = self._default_definition_id
            self._default_definition_json["schemaId"] = str(self._default_schema_json['seqNo'])
            self._default_definition_json["tag"] = req_data
            dt = json.dumps(self._default_definition_json)
        return await ledger.build_cred_def_request(submit_did, dt)
