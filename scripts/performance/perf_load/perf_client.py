import shutil
import json
import os
import asyncio
import signal
from datetime import datetime
from indy import pool, wallet, did, ledger

from perf_load.perf_client_msgs import ClientReady, ClientRun, ClientStop, ClientGetStat, ClientSend, ClientMsg
from perf_load.perf_clientstaistic import ClientStatistic
from perf_load.perf_utils import random_string
from perf_load.perf_req_gen import NoReqDataAvailableException
from perf_load.perf_gen_req_parser import ReqTypeParser


class LoadClient:
    SendResp = 0
    SendTime = 1
    SendSync = 2

    def __init__(self, name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **kwargs):
        self._name = name
        self._stat = ClientStatistic()
        self._send_mode = send_mode
        self._buff_reqs = buff_req
        self._pipe_conn = pipe_conn
        self._pool_name = "pool_{}".format(random_string(24))
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
        self._batch_rate = batch_rate
        self._gen_q = []
        self._send_q = []
        req_class, params = ReqTypeParser.create_req_generator(req_kind)
        self._req_generator = req_class(**params, client_stat=self._stat)
        assert self._req_generator is not None
        self._pool_config = json.dumps(pool_config) if isinstance(pool_config, dict) and pool_config else None
        if self._send_mode == LoadClient.SendResp and self._batch_size > 1:
            raise RuntimeError("Batch size cannot be greater than 1 in response waiting mode")
        if self._send_mode == LoadClient.SendResp and buff_req != 0:
            raise RuntimeError("Cannot pregenerate reqs in response waiting mode")

    def msg(self, fmt: str, *args):
        try:
            self._pipe_conn.send(ClientMsg(fmt, *args))
        except Exception as e:
            print("{} Ready send error {}".format(self._name, e))

    async def pool_open_pool(self, name, config):
        return await pool.open_pool_ledger(name, config)

    async def wallet_create_wallet(self, config, credential):
        await wallet.create_wallet(config, credential)

    async def wallet_open_wallet(self, config, credential):
        return await wallet.open_wallet(config, credential)

    async def did_create_my_did(self, wallet_h, cfg):
        return await did.create_and_store_my_did(wallet_h, cfg)

    async def ledger_sign_req(self, wallet_h, did, req):
        return await ledger.sign_request(wallet_h, did, req)

    async def ledger_submit(self, pool_h, req):
        return await ledger.submit_request(pool_h, req)

    async def pool_close_pool(self, pool_h):
        await pool.close_pool_ledger(pool_h)

    async def pool_protocol_version(self):
        await pool.set_protocol_version(2)

    async def pool_create_config(self, name, cfg):
        await pool.create_pool_ledger_config(name, cfg)

    async def wallet_close(self, wallet_h):
        await wallet.close_wallet(wallet_h)

    async def _init_pool(self, genesis_path):
        await self.pool_protocol_version()
        pool_cfg = json.dumps({"genesis_txn": genesis_path})
        await self.pool_create_config(self._pool_name, pool_cfg)
        self._pool_handle = await self.pool_open_pool(self._pool_name, self._pool_config)

    async def _wallet_init(self, w_key):
        self._wallet_name = "{}_wallet".format(self._pool_name)
        wallet_credential = json.dumps({"key": w_key})
        wallet_config = json.dumps({"id": self._wallet_name})
        await self.wallet_create_wallet(wallet_config, wallet_credential)
        self._wallet_handle = await self.wallet_open_wallet(wallet_config, wallet_credential)

    async def _did_init(self, seed):
        self._test_did, self._test_verk = await self.did_create_my_did(
            self._wallet_handle, json.dumps({'seed': seed[0]}))

    async def _pre_init(self):
        pass

    async def _post_init(self):
        pass

    def _on_pool_create_ext_params(self):
        return {"max_cred_num": self._batch_size}

    async def run_test(self, genesis_path, seed, w_key):
        try:
            await self._pre_init()

            await self._init_pool(genesis_path)
            await self._wallet_init(w_key)
            await self._did_init(seed)

            await self._post_init()

            await self._req_generator.on_pool_create(self._pool_handle, self._wallet_handle, self._test_did,
                                                     self.ledger_sign_req, self.ledger_submit,
                                                     **self._on_pool_create_ext_params())
        except Exception as ex:
            self.msg("{} run_test error {}", self._name, ex)
            self._loop.stop()
            return

        await self.pregen_reqs()

        try:
            self._pipe_conn.send(ClientReady())
        except Exception as e:
            print("{} Ready send error {}".format(self._name, e))
            raise e

    def _on_ClientRun(self, cln_run):
        if self._send_mode == LoadClient.SendTime:
            self._loop.call_soon(self.req_send)

    def _on_ClientSend(self, cln_snd):
        if self._send_mode == LoadClient.SendSync:
            self.req_send(cln_snd.cnt)

    def read_cb(self):
        force_close = False
        try:
            flag = self._pipe_conn.recv()
            if isinstance(flag, ClientStop):
                if self._closing is False:
                    force_close = True
            elif isinstance(flag, ClientRun):
                self.gen_reqs()
                self._on_ClientRun(flag)
            elif isinstance(flag, ClientGetStat):
                self._loop.call_soon(self.send_stat)
            elif isinstance(flag, ClientSend):
                self._on_ClientSend(flag)
        except Exception as e:
            self.msg("{} Error {}", self._name, e)
            force_close = True
        if force_close:
            self._loop.create_task(self.stop_test())

    async def gen_signed_req(self):
        if self._closing is True:
            return
        try:
            req_data, req = await self._req_generator.generate_request(self._test_did)
        except NoReqDataAvailableException:
            self.msg("{} | Cannot generate request since no req data are available.", datetime.now())
            return
        except Exception as e:
            self.msg("{} generate req error {}", self._name, e)
            self._loop.stop()
            raise e
        try:
            sig_req = await self.ledger_sign_req(self._wallet_handle, self._test_did, req)
            self._stat.signed(req_data)
            self._load_client_reqs.append((req_data, sig_req))
        except Exception as e:
            self._stat.reply(req_data, e)
            self._loop.stop()
            raise e
        await self._req_generator.on_request_generated(req_data, sig_req)

    def watch_queues(self):
        if len(self._load_client_reqs) + len(self._gen_q) < self.max_in_bg():
            self._loop.call_soon(self.gen_reqs)

    def check_batch_avail(self, fut):
        self._gen_q.remove(fut)
        if self._send_mode != LoadClient.SendResp:
            self.watch_queues()
        else:
            self.req_send(1)

    def max_in_bg(self):
        return self._buff_reqs + 1

    async def pregen_reqs(self):
        if self._send_mode != LoadClient.SendResp:
            for i in range(self._buff_reqs):
                try:
                    await self.gen_signed_req()
                except NoReqDataAvailableException:
                    self.msg("{} cannot prepare more reqs. Done {}/{}", self._name, i, self._buff_reqs)
                    return

    def gen_reqs(self):
        if self._closing:
            return

        if self._send_mode != LoadClient.SendResp and len(self._gen_q) + len(self._load_client_reqs) > self.max_in_bg():
            return

        builder = self._loop.create_task(self.gen_signed_req())
        builder.add_done_callback(self.check_batch_avail)
        self._gen_q.append(builder)

    async def submit_req_update(self, req_data, req):
        self._stat.sent(req_data, req)
        try:
            resp_or_exp = await self.ledger_submit(self._pool_handle, req)
        except Exception as e:
            resp_or_exp = e
        self._stat.reply(req_data, resp_or_exp)
        await self._req_generator.on_request_replied(req_data, req, resp_or_exp)
        if self._send_mode == LoadClient.SendResp:
            self.gen_reqs()

    def done_submit(self, fut):
        self._send_q.remove(fut)
        if self._send_mode != LoadClient.SendResp:
            self.watch_queues()

    def send_stat(self):
        st = self._stat.dump_stat()
        try:
            self._pipe_conn.send(st)
        except Exception as e:
            print("{} stat send error {}".format(self._name, e))
            raise e

    def req_send(self, cnt: int = None):
        if self._closing:
            return

        if self._send_mode == LoadClient.SendTime:
            self._loop.call_later(self._batch_rate, self.req_send)

        to_snd = cnt or self._batch_size

        if len(self._load_client_reqs) < to_snd:
            self.msg("WARNING need to send {}, but have {}", to_snd, len(self._load_client_reqs))

        for i in range(min(len(self._load_client_reqs), to_snd)):
            req_data, req = self._load_client_reqs.pop()
            sender = self._loop.create_task(self.submit_req_update(req_data, req))
            sender.add_done_callback(self.done_submit)
            self._send_q.append(sender)

    async def stop_test(self):
        self._closing = True
        if len(self._send_q) > 0:
            await asyncio.gather(*self._send_q, return_exceptions=True)
        if len(self._gen_q) > 0:
            await asyncio.gather(*self._gen_q, return_exceptions=True)

        try:
            if self._wallet_handle is not None:
                await self.wallet_close(self._wallet_handle)
        except Exception as e:
            self.msg("{} close_wallet exception: {}", self._name, e)
        try:
            if self._pool_handle is not None:
                await self.pool_close_pool(self._pool_handle)
        except Exception as e:
            self.msg("{} close_pool_ledger exception: {}", self._name, e)

        self._loop.call_soon_threadsafe(self._loop.stop)

        dirs_to_dlt = []
        if self._wallet_name is not None and self._wallet_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/wallet"), self._wallet_name))
        if self._pool_name is not None and self._pool_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/pool"), self._pool_name))

        for d in dirs_to_dlt:
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)

    @classmethod
    def run(cls, name, genesis_path, pipe_conn, seed, batch_size, batch_rate,
            req_kind, buff_req, wallet_key, pool_config, send_mode, mask_sign, ext_set):
        if mask_sign:
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        exts = {}
        if ext_set and isinstance(ext_set, str):
            try:
                exts = json.loads(ext_set)
            except Exception as e:
                print("{} parse ext settings error {}".format(name, e))
                exts = {}

        cln = cls(name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **exts)
        try:
            asyncio.run_coroutine_threadsafe(cln.run_test(genesis_path, seed, wallet_key), loop=cln._loop)
            cln._loop.run_forever()
        except Exception as e:
            print("{} running error {}".format(cln._name, e))
        stat = cln._stat.dump_stat(dump_all=True)
        return stat
