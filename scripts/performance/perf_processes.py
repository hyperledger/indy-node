from abc import ABCMeta, abstractmethod
import copy
import shutil
import json
import time
import datetime
import os
import sys
import asyncio
import argparse
import multiprocessing
import concurrent
import signal
import functools
import base58
import libnacl
import random

from indy import pool, wallet, did, ledger, anoncreds, blob_storage


parser = argparse.ArgumentParser(description='The script generates bunch of txns for the pool with Indy SDK. '
                                 'Detailed description: https://github.com/hyperledger/indy-node/docs/process-based-load-script.md')

parser.add_argument('-c', '--clients', default=0, type=int, required=False, dest='clients',
                    help='Number of client you want to create. '
                         '0 or less means equal to number of available CPUs. '
                         'Default value is 0')


def check_fs(is_dir: bool, fs_name: str):
    pp = os.path.expanduser(fs_name)
    rights = os.W_OK if is_dir else os.R_OK
    chk_func = os.path.isdir if is_dir else os.path.isfile
    size_check = True if is_dir else os.path.getsize(pp) > 0
    if chk_func(pp) and os.access(pp, rights) and size_check:
        return pp
    raise argparse.ArgumentTypeError("{} not found or access error or file empty".format(pp))


parser.add_argument('-g', '--genesis', required=False, dest='genesis_path', type=functools.partial(check_fs, False),
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis")


def check_seed(seed: str):
    if len(seed) == 32:
        return seed
    raise argparse.ArgumentTypeError("Seed must be 32 characters long but provided {}".format(len(seed)))


parser.add_argument('-s', '--seed', type=check_seed, required=False, dest='seed',
                    help='Seed to generate submitter did. Default value is Trustee1',
                    default="000000000000000000000000Trustee1")

parser.add_argument('-k', '--kind', default="nym", type=str, required=False, dest='req_kind',
                    help='Request to send. One of '
                         'nym, schema, attrib, cred_def, revoc_reg_def, revoc_reg_entry, get_nym, '
                         'get_attrib, get_schema, get_cred_def, get_revoc_reg_def, get_revoc_reg, '
                         'get_revoc_reg_delta. '
                         'Default value is "nym". Could be combined in form of JSON array or JSON obj')

parser.add_argument('-n', '--num', default=100, type=int, required=False, dest='batch_size',
                    help='Number of transactions to submit. Default value is 100')

parser.add_argument('-t', '--timeout', default=0, type=float, required=False, dest='batch_timeout',
                    help='Timeout between batches. Default value is 0')

parser.add_argument('-r', '--refresh', default=100, type=int, required=False, dest='refresh_rate',
                    help='Number of replied txns to refresh statistics. Default value is 100')

parser.add_argument('-b', '--bg_tasks', default=30, type=int, required=False, dest='bg_tasks',
                    help='Number of background tasks. Default value is 30')

parser.add_argument('-d', '--directory', default=".", required=False, dest='out_dir',
                    type=functools.partial(check_fs, True),
                    help='Directory to save output files. Default value is "."')

parser.add_argument('--sep', default="|", type=str, required=False, dest='val_sep',
                    help='csv file separator. Default value is "|"')

parser.add_argument('-w', '--wallet_key', default="key", type=str, required=False, dest='wallet_key',
                    help='Wallet encryption key. Default value is "key"')


class ClientStatistic:
    def __init__(self):
        self._req_prep = 0
        self._req_sent = 0
        self._req_succ = 0
        self._req_fail = 0
        self._req_nack = 0
        self._req_rejc = 0

        # inited as something big (datetime.datetime(9999, 1, 1) - datetime.datetime(1970, 1, 1)).total_seconds()
        self._server_min_txn_time = 253370764800
        self._server_max_txn_time = 0

        self._client_stat_reqs = dict()

    def sent_count(self):
        return self._req_sent

    def preparing(self, req_id, test_label: str = ""):
        self._client_stat_reqs.setdefault(req_id, dict())["client_preparing"] = time.time()
        self._client_stat_reqs[req_id]["test_label"] = test_label

    def prepared(self, req_id):
        self._client_stat_reqs.setdefault(req_id, dict())["client_prepared"] = time.time()

    def signed(self, req_id):
        self._client_stat_reqs.setdefault(req_id, dict())["client_signed"] = time.time()
        self._req_prep += 1

    def sent(self, req_id, req):
        self._client_stat_reqs.setdefault(req_id, dict())["client_sent"] = time.time()
        self._client_stat_reqs[req_id]["req"] = req
        self._req_sent += 1

    def reply(self, req_id, reply_or_exception):
        self._client_stat_reqs.setdefault(req_id, dict())["client_reply"] = time.time()
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
                self._client_stat_reqs[req_id]["server_reply"] = server_time
                self._server_min_txn_time = min(self._server_min_txn_time, server_time)
                self._server_max_txn_time = max(self._server_max_txn_time, server_time)
            else:
                self._req_fail += 1
                status = "fail"
            resp = json.dumps(resp)
        else:
            self._req_fail += 1
            status = "fail"
        self._client_stat_reqs[req_id]["status"] = status
        self._client_stat_reqs[req_id]["resp"] = resp

    def dump_stat(self, dump_all: bool = False):
        ret_val = {}
        ret_val["total_prepared"] = self._req_prep
        ret_val["total_sent"] = self._req_sent
        ret_val["total_fail"] = self._req_fail
        ret_val["total_succ"] = self._req_succ
        ret_val["total_nacked"] = self._req_nack
        ret_val["total_rejected"] = self._req_rejc
        srv_time = self._server_max_txn_time - self._server_min_txn_time
        ret_val["server_time"] = srv_time if srv_time >= 0 else 0
        ret_val["reqs"] = []
        reqs = [k for k, v in self._client_stat_reqs.items() if "status" in v or dump_all]
        for r in reqs:
            ret_val["reqs"].append((r, self._client_stat_reqs.pop(r)))
        return ret_val


class RequestGenerator(metaclass=ABCMeta):
    def __init__(self, label: str = "", file_name: str = None, ignore_first_line: bool = True, file_sep: str = "|",
                 client_stat: ClientStatistic = None, **kwargs):
        self._test_label = label
        self._client_stat = client_stat
        if not isinstance(self._client_stat, ClientStatistic):
            raise RuntimeError("Bad Statistic obj")
        random.seed()
        self._data_file = None
        self._file_start_pos = 0
        self._file_sep = file_sep if file_sep else "|"
        if file_name is not None:
            self._data_file = open(check_fs(is_dir=False, fs_name=file_name), "rt")
            if ignore_first_line:
                self._data_file.readline()
                self._file_start_pos = self._data_file.tell()

    # Copied from Plenum
    def random_string(self, sz: int) -> str:
        assert (sz > 0), "Expected random string size cannot be less than 1"
        rv = libnacl.randombytes(sz // 2).hex()
        return rv if sz % 2 == 0 else rv + hex(libnacl.randombytes_uniform(15))[-1]

    # Copied from Plenum
    def rawToFriendly(self, raw):
        return base58.b58encode(raw).decode("utf-8")

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        pass

    def _rand_data(self):
        return self.random_string(32)

    def _from_file_str_data(self, file_str):
        req_id, req_json, reply_json = file_str.split(self._file_sep)
        return reply_json

    def _gen_req_data(self):
        if self._data_file is not None:
            file_str = self._data_file.readline()
            if not file_str:
                self._data_file.seek(self._file_start_pos)
                file_str = self._data_file.readline()
                if not file_str:
                    raise RuntimeError("Data file is empty")
            return self._from_file_str_data(file_str)
        else:
            return self._rand_data()

    @abstractmethod
    async def _gen_req(self, submit_did, req_data):
        pass

    async def generate_request(self, submit_did):
        req_data = self._gen_req_data()
        self._client_stat.preparing(req_data, self._test_label)

        try:
            req = await self._gen_req(submit_did, req_data)
            self._client_stat.prepared(req_data)
        except Exception as ex:
            self._client_stat.reply(req_data, ex)
            raise ex

        return req_data, req


class RGSeqReqs(RequestGenerator):
    def __init__(self, *args, reqs=list(), next_random: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._req_idx = -1
        self._next_idx = self._rand_idx if next_random else self._seq_idx
        if not isinstance(reqs, list):
            raise RuntimeError("Bad Requests sequence provided")
        self._reqs_collection = []
        for reqc, prms in reqs:
            if not issubclass(reqc, RequestGenerator):
                raise RuntimeError("Bad Request class provided")
            cnt = 1
            param = {}
            if isinstance(prms, int) and prms > 0:
                cnt = prms
            elif isinstance(prms, dict):
                cnt = prms.get('count', 1)
                param = prms
            else:
                raise RuntimeError("Bad Request params provided")
            new_req = reqc(*args, **param, **kwargs)
            for i in range(0, cnt):
                self._reqs_collection.append(new_req)
        if len(self._reqs_collection) == 0:
            raise RuntimeError("At least one class should be provided")

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        for req_builder in set(self._reqs_collection):
            await req_builder.on_pool_create(pool_handle, wallet_handle, submitter_did, *args, **kwargs)

    def _seq_idx(self):
        return (self._req_idx + 1) % len(self._reqs_collection)

    def _rand_idx(self):
        return random.randint(0, len(self._reqs_collection) - 1)

    def _gen_req_data(self):
        self._req_idx = self._next_idx()
        return self._reqs_collection[self._req_idx]._gen_req_data()

    async def _gen_req(self, submit_did, req_data):
        return await self._reqs_collection[self._req_idx]._gen_req(submit_did, req_data)


class RGNym(RequestGenerator):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        req_did = self.rawToFriendly(raw)
        return req_did

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        req_did = json.loads(req_json)['result']['txn']['data']['dest']
        return req_did

    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_nym_request(submit_did, req_data, None, None, None)


class RGGetNym(RGNym):
    async def _gen_req(self, submit_did, req_data):
        return await ledger.build_get_nym_request(submit_did, req_data)


class RGSchema(RequestGenerator):
    async def _gen_req(self, submit_did, req_data):
        _, schema_json = await anoncreds.issuer_create_schema(submit_did, req_data,
                                                              "1.0", json.dumps(["name", "age", "sex", "height"]))
        schema_request = await ledger.build_schema_request(submit_did, schema_json)
        return schema_request

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        schema_id = json.loads(req_json)['result']['txnMetadata']['txnId']
        return schema_id


class RGGetSchema(RGSchema):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        target_did = self.rawToFriendly(raw)
        schema_marker = '02'
        name = super()._rand_data()
        version = '1.0'
        schema_id = ':'.join([target_did, schema_marker, name, version])
        return schema_id

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_schema_request(submit_did, req_data)
        return req


class RGAttrib(RequestGenerator):
    async def _gen_req(self, submit_did, req_data):
        raw_attr = json.dumps({req_data: req_data})
        attr_request = await ledger.build_attrib_request(submit_did, submit_did, None, raw_attr, None)
        return attr_request

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        raw = json.loads(req_json)['result']['txn']['data']['raw']
        return raw


class RGGetAttrib(RGAttrib):
    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_attrib_request(submit_did, submit_did, req_data, None, None)
        return req


class RGGetDefinition(RequestGenerator):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        origin = self.rawToFriendly(raw)
        cred_def_marker = '03'
        signature_type = 'CL'
        schema_id = '1'
        cred_def_id = ':'.join([origin, cred_def_marker, signature_type, schema_id])
        return cred_def_id

    def _from_file_str_data(self, file_str):
        req_json = super()._from_file_str_data(file_str)
        cred_def_id = json.loads(req_json)['result']['txnMetadata']['txnId']
        return cred_def_id

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_cred_def_request(submit_did, req_data)
        return req


class RGDefinition(RGGetDefinition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._wallet_handle = None
        self._default_schema_json = None

    def _rand_data(self):
        return self.random_string(32)

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        self._wallet_handle = wallet_handle
        _, self._default_schema_json = await anoncreds.issuer_create_schema(
            submitter_did, self.random_string(32), "1.0", json.dumps(["name", "age", "sex", "height"]))
        schema_request = await ledger.build_schema_request(submitter_did, self._default_schema_json)
        resp = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, schema_request)
        resp = json.loads(resp)
        seqno =\
            resp.get('result', {}).get('seqNo', None) or\
            resp.get('result', {}).get('txnMetadata', {}).get('seqNo', None)
        self._default_schema_json = json.loads(self._default_schema_json)
        # TODO: Instead of manually patching schema json GET_SCHEMA should be used
        self._default_schema_json['seqNo'] = seqno
        self._default_schema_json = json.dumps(self._default_schema_json)

    async def _gen_req(self, submit_did, req_data):
        _, definition_json = await anoncreds.issuer_create_and_store_credential_def(
            self._wallet_handle, submit_did, self._default_schema_json,
            req_data, "CL", json.dumps({"support_revocation": True}))
        return await ledger.build_cred_def_request(submit_did, definition_json)


class RGDefRevoc(RGDefinition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_definition_id = None
        self._default_definition_json = None

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, *args, **kwargs)

        self._default_definition_id, self._default_definition_json =\
            await anoncreds.issuer_create_and_store_credential_def(
                wallet_handle, submitter_did, self._default_schema_json,
                self.random_string(32), "CL", json.dumps({"support_revocation": True}))
        definition_request = await ledger.build_cred_def_request(submitter_did, self._default_definition_json)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, definition_request)

    async def _gen_req(self, submit_did, req_data):
        tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
        tails_writer = await blob_storage.open_writer('default', tails_writer_config)
        _, revoc_reg_def_json, revoc_reg_entry_json = await anoncreds.issuer_create_and_store_revoc_reg(
            self._wallet_handle, submit_did, "CL_ACCUM", req_data,
            json.loads(self._default_definition_json)['id'],
            json.dumps({"max_cred_num": 5, "issuance_type": "ISSUANCE_BY_DEFAULT"}),
            tails_writer)
        return await ledger.build_revoc_reg_def_request(submit_did, revoc_reg_def_json)


class RGGetDefRevoc(RGGetDefinition):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        submitter_did = self.rawToFriendly(raw)
        cred_def_marker = '03'
        signature_type = 'CL'
        schema_id = '1'
        cred_def_id = ':'.join([submitter_did, cred_def_marker, signature_type, schema_id])
        revoc_reg_marker = '04'
        revoc_def_type = 'CL_ACCUM'
        revoc_def_tag = 'reg1'
        def_revoc_id = ':'.join([submitter_did, revoc_reg_marker, cred_def_id, revoc_def_type, revoc_def_tag])
        return def_revoc_id

    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_revoc_reg_def_request(submit_did, req_data)
        return req


class RGEntryRevoc(RGDefRevoc):
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

    async def on_pool_create(self, pool_handle, wallet_handle, submitter_did, *args, **kwargs):
        await super().on_pool_create(pool_handle, wallet_handle, submitter_did, *args, **kwargs)
        max_cred_num = kwargs["max_cred_num"] if "max_cred_num" in kwargs else 100

        tails_writer_config = json.dumps({'base_dir': 'tails', 'uri_pattern': ''})
        tails_writer = await blob_storage.open_writer('default', tails_writer_config)
        self._blob_storage_reader_cfg_handle = await blob_storage.open_reader('default', tails_writer_config)
        self._default_revoc_reg_def_id, self._default_revoc_reg_def_json, self._default_revoc_reg_entry_json =\
            await anoncreds.issuer_create_and_store_revoc_reg(
                wallet_handle, submitter_did, "CL_ACCUM", self.random_string(32),
                json.loads(self._default_definition_json)['id'],
                json.dumps({"max_cred_num": max_cred_num, "issuance_type": "ISSUANCE_ON_DEMAND"}),
                tails_writer)
        def_revoc_request = await ledger.build_revoc_reg_def_request(submitter_did, self._default_revoc_reg_def_json)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, def_revoc_request)

        entry_revoc_request = await ledger.build_revoc_reg_entry_request(
            submitter_did, self._default_revoc_reg_def_id, "CL_ACCUM", self._default_revoc_reg_entry_json)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, entry_revoc_request)

    async def _gen_req(self, submit_did, req_data):
        cred_offer_json = await anoncreds.issuer_create_credential_offer(
            self._wallet_handle, self._default_definition_id)
        master_secret_id = await anoncreds.prover_create_master_secret(
            self._wallet_handle, master_secret_name='')
        cred_req_json, _ = await anoncreds.prover_create_credential_req(
            self._wallet_handle, submit_did, cred_offer_json, self._default_definition_json, master_secret_id)
        _, _, revoc_reg_delta_json = await anoncreds.issuer_create_credential(
            self._wallet_handle, cred_offer_json, cred_req_json, self._default_cred_values_json,
            self._default_revoc_reg_def_id, self._blob_storage_reader_cfg_handle)
        return await ledger.build_revoc_reg_entry_request(
            submit_did, self._default_revoc_reg_def_id, "CL_ACCUM", revoc_reg_delta_json)


class RGGetEntryRevoc(RGGetDefinition):
    def _rand_data(self):
        raw = libnacl.randombytes(16)
        submitter_did = self.rawToFriendly(raw)
        cred_def_marker = '03'
        signature_type = 'CL'
        schema_id = str(random.randint(1, 100))
        cred_def_id = ':'.join([submitter_did, cred_def_marker, signature_type, schema_id])
        revoc_reg_marker = '04'
        revoc_def_type = 'CL_ACCUM'
        revoc_def_tag = 'reg1'
        def_revoc_id = ':'.join([submitter_did, revoc_reg_marker, cred_def_id, revoc_def_type, revoc_def_tag])
        entry_revoc_marker = '05'
        entry_revoc_id = ':'.join([submitter_did, entry_revoc_marker, def_revoc_id])
        return entry_revoc_id

    async def _gen_req(self, submit_did, req_data):
        timestamp = int(time.time())
        req = await ledger.build_get_revoc_reg_request(submit_did, req_data, timestamp)
        return req


class RGGetRevocRegDelta(RGGetEntryRevoc):
    async def _gen_req(self, submit_did, req_data):
        req = await ledger.build_get_revoc_reg_delta_request(submit_did, req_data, None, int(time.time()))
        return req


def create_req_generator(req_kind_arg):
    supported_requests = {"nym": RGNym, "schema": RGSchema, "attrib": RGAttrib,
                          "cred_def": RGDefinition, "revoc_reg_def": RGDefRevoc,
                          "revoc_reg_entry": RGEntryRevoc,
                          "get_nym": RGGetNym, "get_attrib": RGGetAttrib,
                          "get_schema": RGGetSchema, "get_cred_def": RGGetDefinition,
                          "get_revoc_reg_def": RGGetDefRevoc, "get_revoc_reg": RGGetEntryRevoc,
                          "get_revoc_reg_delta": RGGetRevocRegDelta}
    if req_kind_arg in supported_requests:
        return supported_requests[req_kind_arg], {}
    try:
        reqs = json.loads(req_kind_arg)
    except Exception as e:
        raise RuntimeError("Invalid parameter format")

    def _parse_single(req_kind, prms):
        if req_kind is None and isinstance(prms, dict):
            req_crt = [k for k in prms.keys() if k in supported_requests]
            if len(req_crt) == 1:
                tmp_params = copy.copy(prms)
                tmp_params.pop(req_crt[0])
                return supported_requests[req_crt[0]], tmp_params
        if isinstance(req_kind, str) and req_kind in supported_requests:
            return supported_requests[req_kind], prms
        if isinstance(req_kind, str) and req_kind not in supported_requests:
            return _parse_single(None, prms)
        if isinstance(req_kind, dict) and len(req_kind.keys()) == 1:
            k = list(req_kind)[0]
            v = req_kind[k]
            return _parse_single(k, v)
        raise RuntimeError("Invalid parameter format")

    ret_reqs = []
    randomizing = False
    if isinstance(reqs, dict):
        randomizing = True
        for k, v in reqs.items():
            ret_reqs.append(_parse_single(k, v))
    elif isinstance(reqs, list):
        randomizing = False
        for r in reqs:
            ret_reqs.append(_parse_single(r, {}))
    if len(ret_reqs) == 1:
        req = ret_reqs[0][0]
        par = {} if isinstance(ret_reqs[0][1], int) else ret_reqs[0][1]
        return req, par
    else:
        return RGSeqReqs, {'next_random': randomizing, 'reqs': ret_reqs}


class LoadClient:
    def __init__(self, name, pipe_conn, batch_size, batch_timeout, req_kind, bg_tasks, refresh):
        self._name = name
        self._refresh = refresh
        self._stat = ClientStatistic()
        self._gen_lim = bg_tasks // 2
        self._send_lim = bg_tasks // 2
        self._pipe_conn = pipe_conn
        self._pool_name = "pool_{}".format(os.getpid())
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._pool_handle = None
        self._wallet_name = None
        self._wallet_handle = None
        self._test_did = None
        self._test_verk = None
        self._load_client_reqs = []
        self._loop.add_reader(self._pipe_conn, self.read_cb)
        self._closing = False
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout
        self._gen_q = []
        self._send_q = []
        req_class, params = create_req_generator(req_kind)
        self._req_generator = req_class(**params, client_stat=self._stat)
        assert self._req_generator is not None
        self._rest_to_sent = batch_size

    async def run_test(self, genesis_path, seed, w_key):
        try:
            pool_cfg = json.dumps({"genesis_txn": genesis_path})

            # TODO: remove after latest changes committed
            await pool.set_protocol_version(2)

            await pool.create_pool_ledger_config(self._pool_name, pool_cfg)
            self._pool_handle = await pool.open_pool_ledger(self._pool_name, None)
            self._wallet_name = "{}_wallet".format(self._pool_name)
            wallet_credential = json.dumps({"key": w_key})
            await wallet.create_wallet(self._pool_name, self._wallet_name, None, None, wallet_credential)
            self._wallet_handle = await wallet.open_wallet(self._wallet_name, None, wallet_credential)
            self._test_did, self._test_verk = await did.create_and_store_my_did(self._wallet_handle, json.dumps({'seed': seed}))
            await self._req_generator.on_pool_create(self._pool_handle, self._wallet_handle,
                                                     self._test_did, max_cred_num=self._batch_size)
        except Exception as ex:
            print("{} run_test error {}".format(self._name, ex))
            self._loop.stop()
            raise ex

        self.gen_reqs()

    def read_cb(self):
        force_close = False
        try:
            flag = self._pipe_conn.recv()
            if isinstance(flag, bool) and flag is False:
                if self._closing is False:
                    force_close = True
        except Exception as e:
            print("{} Error {}".format(self._name, e))
            force_close = True
        if force_close:
            self._loop.create_task(self.stop_test())

    async def gen_signed_req(self):
        if self._closing is True:
            return
        try:
            req_id, req = await self._req_generator.generate_request(self._test_did)
        except Exception as e:
            print("{} generate req error {}".format(self._name, e))
            self._loop.stop()
            raise e
        try:
            sig_req = await ledger.sign_request(self._wallet_handle, self._test_did, req)
            self._stat.signed(req_id)
            self._load_client_reqs.append((req_id, sig_req))
        except Exception as e:
            self._stat.reply(req_id, e)
            self._loop.stop()
            raise e

    def watch_queues(self):
        if len(self._load_client_reqs) + len(self._gen_q) < self._batch_size:
            self._loop.call_soon(self.gen_reqs)
        if len(self._load_client_reqs) > 0 and len(self._send_q) < self._send_lim:
            self._loop.call_soon(self.req_send)

    def check_batch_avail(self, fut):
        self._gen_q.remove(fut)
        self.watch_queues()

    def max_in_bg(self):
        return min(500, 3 * self._batch_size)

    def gen_reqs(self):
        if self._closing:
            return

        avail_gens = self._gen_lim - len(self._gen_q)
        if avail_gens <= 0 or len(self._gen_q) + len(self._load_client_reqs) > self.max_in_bg():
            return

        for i in range(0, min(avail_gens, self._batch_size)):
            builder = self._loop.create_task(self.gen_signed_req())
            builder.add_done_callback(self.check_batch_avail)
            self._gen_q.append(builder)

    async def submit_req_update(self, req_id, req):
        self._stat.sent(req_id, req)
        try:
            resp_or_exp = await ledger.submit_request(self._pool_handle, req)
        except Exception as e:
            resp_or_exp = e
        self._stat.reply(req_id, resp_or_exp)

    def done_submit(self, fut):
        self._send_q.remove(fut)
        self.watch_queues()
        if self._stat.sent_count() % self._refresh == 0:
            self._loop.call_soon(self.send_stat)

    def send_stat(self):
        st = self._stat.dump_stat()
        try:
            self._pipe_conn.send(st)
        except Exception as e:
            print("{} stat send error {}".format(self._name, e))
            raise e

    def req_send(self, start_new_batch: bool = False):
        if self._closing:
            return

        if start_new_batch:
            self._rest_to_sent = self._batch_size

        avail_sndrs = self._send_lim - len(self._send_q)
        if avail_sndrs <= 0 or self._rest_to_sent <= 0:
            return

        if self._rest_to_sent > 0:
            to_snd = min(len(self._load_client_reqs), avail_sndrs, self._rest_to_sent)
            for i in range(0, to_snd):
                req_id, req = self._load_client_reqs.pop()
                sender = self._loop.create_task(self.submit_req_update(req_id, req))
                sender.add_done_callback(self.done_submit)
                self._send_q.append(sender)
            self._rest_to_sent -= to_snd

        if self._rest_to_sent <= 0:
            if self._batch_timeout == 0:
                self._loop.create_task(self.stop_test())
            else:
                self._loop.call_later(self._batch_timeout, functools.partial(self.req_send, start_new_batch=True))

    async def stop_test(self):
        self._closing = True
        if len(self._send_q) > 0:
            await asyncio.gather(*self._send_q, return_exceptions=True)

        try:
            if self._wallet_handle is not None:
                await wallet.close_wallet(self._wallet_handle)
        except Exception as e:
            print("{} close_wallet exception: {}".format(self._name, e))
        try:
            if self._pool_handle is not None:
                await pool.close_pool_ledger(self._pool_handle)
        except Exception as e:
            print("{} close_pool_ledger exception: {}".format(self._name, e))

        self._loop.call_soon_threadsafe(self._loop.stop)

        dirs_to_dlt = []
        if self._wallet_name is not None and self._wallet_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/wallet"), self._wallet_name))
        if self._pool_name is not None and self._pool_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/pool"), self._pool_name))

        for d in dirs_to_dlt:
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)


def run_client(name, genesis_path, pipe_conn, seed, batch_size, batch_timeout, req_kind, bg_tasks, refresh, wallet_key):
    cln = LoadClient(name, pipe_conn, batch_size, batch_timeout, req_kind, bg_tasks, refresh)
    try:
        asyncio.run_coroutine_threadsafe(cln.run_test(genesis_path, seed, wallet_key), loop=cln._loop)
        cln._loop.run_forever()
    except Exception as e:
        print("{} running error {}".format(cln._name, e))
    stat = cln._stat.dump_stat(dump_all=True)
    return stat


class ClientRunner:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn
        self.closed = False
        self.total_sent = 0
        self.total_succ = 0
        self.total_failed = 0
        self.total_nack = 0
        self.total_reject = 0
        self.total_server_time = 0

    def stop_client(self):
        self.closed = True

    def is_finished(self):
        return self.closed

    def refresh_stat(self, stat):
        if not isinstance(stat, dict):
            return
        self.total_sent = stat.get("total_sent", self.total_sent)
        self.total_succ = stat.get("total_succ", self.total_succ)
        self.total_failed = stat.get("total_fail", self.total_failed)
        self.total_nack = stat.get("total_nacked", self.total_nack)
        self.total_reject = stat.get("total_rejected", self.total_reject)
        self.total_server_time = stat.get("server_time", self.total_server_time)


class TestRunner:
    def __init__(self):
        self._clients = dict()  # key process future; value ClientRunner
        self._loop = asyncio.get_event_loop()
        self._out_dir = ""
        self._succ_f = None
        self._failed_f = None
        self._total_f = None
        self._nacked_f = None
        self._value_separator = "|"

    def process_reqs(self, stat):
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f
        if not isinstance(stat, dict):
            return
        reqs = stat.get("reqs", [])
        for (r_id, r_data) in reqs:
            # ["label", "id", "status", "client_preparing", "client_prepared", "client_sent", "client_reply", "server_reply"]
            status = r_data.get("status", "")
            print(r_data.get("test_label", ""), r_id, status, r_data.get("client_preparing", 0), r_data.get("client_prepared", 0), r_data.get("client_signed", 0),
                  r_data.get("client_sent", 0), r_data.get("client_reply", 0), r_data.get("server_reply", 0),
                  file=self._total_f, sep=self._value_separator)

            # ["id", "req", "resp"]
            if status == "succ":
                print(r_id, r_data.get("req", ""), r_data.get("resp", ""), file=self._succ_f, sep=self._value_separator)
            elif status in ["nack", "reject"]:
                print(r_id, r_data.get("req", ""), r_data.get("resp", ""), file=self._nacked_f, sep=self._value_separator)
            else:
                print(r_id, r_data.get("req", ""), r_data.get("resp", ""), file=self._failed_f, sep=self._value_separator)

    def sig_handler(self, sig):
        for prc, cln in self._clients.items():
            try:
                if not cln.is_finished():
                    cln.conn.send(False)
                if sig == signal.SIGTERM:
                    prc.cancel()
            except Exception as e:
                print("Sent stop to client {} error {}".format(cln.name, e))

    def read_client_cb(self, prc):
        try:
            r_data = self._clients[prc].conn.recv()
            if isinstance(r_data, dict):
                self._clients[prc].refresh_stat(r_data)
                self.process_reqs(r_data)

                print(self.get_refresh_str(), end="\r")
            else:
                print("Recv garbage {} from {}".format(r_data, self._clients[prc].name))
        except Exception as e:
            print("{} read_client_cb error {}".format(self._clients[prc].name, e))
            self._clients[prc].conn = None

    def client_done(self, client):
        try:
            last_stat = client.result()
            self._clients[client].refresh_stat(last_stat)
            self.process_reqs(last_stat)
        except Exception as e:
            print("Client Error", e)

        self._clients[client].stop_client()
        self._loop.remove_reader(self._clients[client].conn)

        is_closing = all([cln.is_finished() for cln in self._clients.values()])

        if is_closing:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def get_refresh_str(self):
        clients = 0
        total_server_time = 0
        total_sent = 0
        total_succ = 0
        total_failed = 0
        total_nack = 0
        total_reject = 0

        for cln in self._clients.values():
            if not cln.is_finished():
                clients += 1
            total_sent += cln.total_sent
            total_succ += cln.total_succ
            total_failed += cln.total_failed
            total_nack += cln.total_nack
            total_reject += cln.total_reject
            total_server_time = max(total_server_time, cln.total_server_time)
        print_str = "Server Time: {} Sent: {} Succ: {} Failed: {} Nacked: {} Rejected: {} Clients Alive {}".format(
            total_server_time, total_sent, total_succ, total_failed, total_nack, total_reject, clients)
        return print_str

    def prepare_fs(self, out_dir, test_dir_name):
        self._out_dir = os.path.join(out_dir, test_dir_name)
        if not os.path.exists(self._out_dir):
            os.makedirs(self._out_dir)

        with open(os.path.join(self._out_dir, "args"), "w") as f:
            f.writelines([" ".join(sys.argv)])

        self._succ_f = open(os.path.join(self._out_dir, "successful"), "w")
        self._failed_f = open(os.path.join(self._out_dir, "failed"), "w")
        self._nacked_f = open(os.path.join(self._out_dir, "nack_reject"), "w")
        self._total_f = open(os.path.join(self._out_dir, "total"), "w")
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f

        print("id", "req", "resp", file=self._failed_f, sep=self._value_separator)
        print("id", "req", "resp", file=self._nacked_f, sep=self._value_separator)
        print("id", "req", "resp", file=self._succ_f, sep=self._value_separator)
        print("label", "id", "status", "client_preparing", "client_prepared",
              "client_signed", "client_sent", "client_reply", "server_reply",
              file=self._total_f, sep=self._value_separator)

    def close_fs(self):
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f
        self._failed_f.close()
        self._total_f.close()
        self._succ_f.close()
        self._nacked_f.close()

    def test_run(self, args):
        proc_count = args.clients if args.clients > 0 else multiprocessing.cpu_count()
        refresh = args.refresh_rate if args.refresh_rate > 0 else 100
        bg_tasks = args.bg_tasks if args.bg_tasks > 1 else 300
        start_date = datetime.datetime.now()
        value_separator = args.val_sep if args.val_sep != "" else "|"
        print("Number of client         ", proc_count)
        print("Path to genesis txns file", args.genesis_path)
        print("Seed                     ", args.seed)
        print("Batch size               ", args.batch_size)
        print("Timeout between batches  ", args.batch_timeout)
        print("Request kind             ", args.req_kind)
        print("Refresh rate, txns       ", refresh)
        print("Background tasks         ", bg_tasks)
        print("Output directory         ", args.out_dir)
        print("Value Separator          ", value_separator)
        print("Wallet Key               ", args.wallet_key)
        print("Started At               ", start_date)

        self._value_separator = value_separator

        self.prepare_fs(args.out_dir, "load_test_{}".format(start_date.strftime("%Y%m%d_%H%M%S")))

        self._loop.add_signal_handler(signal.SIGTERM, functools.partial(self.sig_handler, signal.SIGTERM))
        self._loop.add_signal_handler(signal.SIGINT, functools.partial(self.sig_handler, signal.SIGINT))

        executor = concurrent.futures.ProcessPoolExecutor(proc_count)
        for i in range(0, proc_count):
            rd, wr = multiprocessing.Pipe()
            prc_name = "LoadClient_{}".format(i)
            prc = executor.submit(run_client, prc_name, args.genesis_path, wr,
                                  args.seed, args.batch_size, args.batch_timeout,
                                  args.req_kind, bg_tasks, refresh, args.wallet_key)
            prc.add_done_callback(self.client_done)
            self._loop.add_reader(rd, self.read_client_cb, prc)
            self._clients[prc] = ClientRunner(prc_name, rd)

        print("Started", proc_count, "processes")

        self._loop.run_forever()

        self._loop.remove_signal_handler(signal.SIGTERM)
        self._loop.remove_signal_handler(signal.SIGINT)

        print("")
        print("DONE At", datetime.datetime.now())
        print(self.get_refresh_str())
        self.close_fs()


if __name__ == '__main__':
    args = parser.parse_args()
    tr = TestRunner()
    tr.test_run(args)
