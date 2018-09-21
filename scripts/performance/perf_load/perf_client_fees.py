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
from perf_load.perf_client import LoadClient

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


class LoadClientFees(LoadClient):
    __initiated_plugins = set()

    def __init__(self, name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **kwargs):
        super().__init__(name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, **kwargs)
        self._trustee_dids = []

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

    async def run_test(self, genesis_path, seed, w_key):
        try:
            pool_cfg = json.dumps({"genesis_txn": genesis_path})

            await self.pool_protocol_version()

            await self.pool_create_config(self._pool_name, pool_cfg)
            self._pool_handle = await self.pool_open_pool(self._pool_name, self._pool_config)
            self._wallet_name = "{}_wallet".format(self._pool_name)
            wallet_credential = json.dumps({"key": w_key})
            wallet_config = json.dumps({"id": self._wallet_name})
            await self.wallet_create_wallet(wallet_config, wallet_credential)
            self._wallet_handle = await self.wallet_open_wallet(wallet_config, wallet_credential)




            self._test_did, self._test_verk = await self.did_create_my_did(self._wallet_handle, json.dumps({'seed': seed}))
            await self._req_generator.on_pool_create(self._pool_handle, self._wallet_handle,
                                                     self._test_did, self.ledger_sign_req, self.ledger_submit,
                                                     max_cred_num=self._batch_size)
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
