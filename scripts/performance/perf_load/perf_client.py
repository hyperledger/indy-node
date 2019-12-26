import shutil
import json
import os
import asyncio
import signal
import logging
from typing import Optional, Tuple

from indy import pool, wallet, did, ledger

from perf_load.perf_client_msgs import ClientReady, ClientRun, ClientStop, ClientGetStat, ClientSend
from perf_load.perf_clientstaistic import ClientStatistic
from perf_load.perf_utils import random_string, logger_init, ensure_is_reply
from perf_load.perf_req_gen import NoReqDataAvailableException
from perf_load.perf_gen_req_parser import ReqTypeParser

TRUSTEE_ROLE_CODE = "0"


class LoadClient:
    SendResp = 0
    SendTime = 1
    SendSync = 2

    TestAcceptanceMechanism = 'test'
    TestAcceptanceMechanismVersion = 'test_version'

    def __init__(self, name, pipe_conn, batch_size, batch_rate, req_kind, buff_req, pool_config, send_mode, short_stat,
                 **kwargs):
        self._name = name
        self._stat = ClientStatistic(short_stat)
        self._send_mode = send_mode
        self._buff_reqs = buff_req
        self._pipe_conn = pipe_conn
        self._pool_name = "pool_{}".format(random_string(24))
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._pool_handle = None
        self._wallet_name = None
        self._wallet_handle = None
        self._trustee_dids = []
        self._req_num_of_trustees = kwargs.get("trustees_num", 1)
        self._set_auth_rule = kwargs.get("set_auth_rules", False)
        self._test_did = None
        self._test_verk = None
        self._taa_text = None
        self._taa_version = None
        self._taa_time = None
        self._load_client_reqs = []
        self._loop.add_reader(self._pipe_conn, self.read_cb)
        self._closing = False
        self._batch_size = batch_size
        self._batch_rate = batch_rate
        self._auth_rule_metadata = {}
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
        self._logger = logging.getLogger(self._name)

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
        self._logger.info("_init_pool {}".format(genesis_path))
        await self.pool_protocol_version()
        pool_cfg = json.dumps({"genesis_txn": genesis_path})
        await self.pool_create_config(self._pool_name, pool_cfg)
        self._pool_handle = await self.pool_open_pool(self._pool_name, self._pool_config)
        self._logger.info("_init_pool done")

    async def _wallet_init(self, w_key):
        self._logger.info("_wallet_init {}".format(w_key))
        self._wallet_name = "{}_wallet".format(self._pool_name)
        wallet_credential = json.dumps({"key": w_key})
        wallet_config = json.dumps({"id": self._wallet_name})
        await self.wallet_create_wallet(wallet_config, wallet_credential)
        self._wallet_handle = await self.wallet_open_wallet(wallet_config, wallet_credential)
        self._logger.info("_wallet_init done")

    async def _did_init(self, seed, taa_text, taa_version):
        self._logger.info("_did_init {}".format(seed))

        if len(set(seed)) < self._req_num_of_trustees:
            raise RuntimeError("Number of trustee seeds must be eq to {}".format(self._req_num_of_trustees))
        if len(set(seed)) != len(seed):
            raise RuntimeError("Duplicated seeds not allowed")

        for s in seed:
            self._test_did, self._test_verk = await self.did_create_my_did(
                self._wallet_handle, json.dumps({'seed': s}))
            await self._ensure_trustee(self._test_did)

            # TODO: This needs serious refactoring
            if self._taa_text is None:
                await self._taa_init(taa_text, taa_version)

        self._logger.info("_did_init done")

    async def _taa_init(self, text, version):
        self._logger.info("_taa_init {} {}".format(text, version))

        if text != "":
            await self._taa_aml_init()

        while True:
            # Continuously check for latest TAA and break when reaching desired state
            current_text, current_version, current_time = await self._get_taa()

            # If we don't need TAA and ledger doesn't have TAA then we don't care about other details
            if text == "" and current_text == "":
                self._taa_text = ""
                break

            # If we need TAA and all details match we're good to go
            if current_text == text and current_version == version:
                self._taa_text = current_text
                self._taa_version = current_version
                self._taa_time = current_time + 1  # We are "signing" just 1 second after TAA created
                break

            # Check that we don't already have different TAA with same version
            expected_text, expected_version, _ = await self._get_taa(version)
            if expected_text != text and expected_version == version:
                raise RuntimeError("Ledger already contains different TAA with same version ")

            # Try to set taa
            if text != "":
                set_taa = await ledger.build_txn_author_agreement_request(self._test_did, text, version,
                                                                          ratification_ts=42)
            else:
                set_taa = await ledger.build_disable_all_txn_author_agreements_request(self._test_did)
            await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, set_taa)

        self._logger.info("_taa_init done")

    async def _taa_aml_init(self):
        self._logger.info("_taa_aml_init")

        while True:
            # Continuously check for latest TAA
            get_aml = await ledger.build_get_acceptance_mechanisms_request(self._test_did, None, None)
            reply = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did,
                                                         get_aml)
            ensure_is_reply(reply)
            data = json.loads(reply)['result']['data']
            current_aml = data.get('aml', {}) if data else {}

            # We reached desired state
            if self.TestAcceptanceMechanism in current_aml:
                break

            # Check whether we can reach desired AML state at all
            if data is not None:
                raise RuntimeError("There is already incompatible TAA AML written to ledger")

            # Try to set aml
            set_aml = await ledger.build_acceptance_mechanisms_request(self._test_did,
                                                                       json.dumps({self.TestAcceptanceMechanism: {}}),
                                                                       self.TestAcceptanceMechanismVersion, None)
            await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, set_aml)

        self._logger.info("_taa_aml_init done")

    async def _is_trustee(self, did) -> Optional[bool]:
        """
        :return: None, if DID is not public, otherwise bool indicating whether this DID have trustee rights
        """
        get_nym_req = await ledger.build_get_nym_request(did, did)
        get_nym_resp = await ledger.sign_and_submit_request(
            self._pool_handle, self._wallet_handle, did, get_nym_req)
        get_nym_resp_obj = json.loads(get_nym_resp)
        ensure_is_reply(get_nym_resp_obj)
        data_f = get_nym_resp_obj["result"].get("data", None)
        if data_f is None:
            return None
        res_data = json.loads(data_f)
        return res_data["role"] == TRUSTEE_ROLE_CODE

    async def _ensure_trustee(self, did):
        while True:
            # Continuously check for trustee status and break when reaching desired status
            is_trustee = await self._is_trustee(did)

            # If we are trustee we're good to go
            if is_trustee:
                self._trustee_dids.append(did)
                return

            # If we are not trustee then we're in trouble
            if is_trustee is False:
                raise Exception("Submitter role must be TRUSTEE")

            # Now we need to create a trustee, but need another one to do so
            if len(self._trustee_dids) < 1:
                raise Exception("Cannot create new trustees without initial one")

            # Fire and forget create trustee, will check status on next loop iteration
            nym_req = await ledger.build_nym_request(self._trustee_dids[0],
                                                     self._test_did, self._test_verk,
                                                     None, "TRUSTEE")
            nym_req = await self.append_taa_acceptance(nym_req)
            await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle,
                                                 self._trustee_dids[0], nym_req)

    async def _get_taa(self, version: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        options = json.dumps({'version': version}) if version else None
        request = await ledger.build_get_txn_author_agreement_request(self._test_did, options)
        reply = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, request)
        ensure_is_reply(reply)

        result = json.loads(reply)['result']
        if result['data'] is None:
            return "", "", None

        return result['data']['text'], result['data']['version'], result['data']['ratification_ts']

    async def _pool_auth_rules_init(self):
        if not self._set_auth_rule:
            self._logger.info("Auth rules are not required to be set")
            return

        self._logger.info("Setting auth rules...")
        get_auth_rule_req = await ledger.build_get_auth_rule_request(self._test_did, None, None, None, None, None)
        get_auth_rule_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, get_auth_rule_req)
        ensure_is_reply(get_auth_rule_resp)

        get_auth_rule_resp = json.loads(get_auth_rule_resp)
        data_f = get_auth_rule_resp["result"].get("data", [])
        if not data_f:
            self._logger.warning("No auth rules found")
            return

        for auth_rule in data_f:
            try:
                metadata_addition = self._auth_rule_metadata.get(auth_rule['auth_type'], None)
                if metadata_addition:
                    update_constraint(auth_rule['constraint'], metadata_addition)
                auth_rule_req = await ledger.build_auth_rule_request(
                    self._test_did,
                    txn_type=auth_rule['auth_type'],
                    action=auth_rule['auth_action'],
                    field=auth_rule['field'],
                    old_value=auth_rule.get('old_value'),
                    new_value=auth_rule.get('new_value'),
                    constraint=json.dumps(auth_rule['constraint']),
                )
                auth_rule_resp = await ledger.sign_and_submit_request(self._pool_handle, self._wallet_handle, self._test_did, auth_rule_req)
                ensure_is_reply(auth_rule_resp)
            except Exception:
                self._logger.exception(
                    "Failed to set auth rule with the following parameters: {} "
                    .format(auth_rule)
                )
                raise
        self._logger.info("_pool_auth_rules_init done")

    async def _pre_init(self):
        pass

    async def _post_init(self):
        # This is called here and not in run_test because LoadClientFees needs to do some setup
        # before pool_auth_rules_init is called.
        # TODO: Move this into run_test after call to _post_init,
        #  rename _post_init to _pre_auth_rules_init or _post_did_init?
        await self._pool_auth_rules_init()

    def _on_pool_create_ext_params(self):
        return {"max_cred_num": self._batch_size,
                "taa_text": self._taa_text,
                "taa_version": self._taa_version,
                "taa_mechanism": self.TestAcceptanceMechanism,
                "taa_time": self._taa_time}

    async def run_test(self, genesis_path, seed, w_key, taa_text, taa_version):
        self._logger.info("run_test genesis_path {}, seed {}, w_key {}".format(genesis_path, seed, w_key))
        try:
            await self._pre_init()

            await self._init_pool(genesis_path)
            await self._wallet_init(w_key)
            # TODO: This needs serious refactoring
            await self._did_init(seed, taa_text, taa_version)

            await self._post_init()

            self._logger.info("call _req_generator.on_pool_create")
            await self._req_generator.on_pool_create(self._pool_handle, self._wallet_handle, self._test_did,
                                                     self.ledger_sign_req, self.ledger_submit,
                                                     **self._on_pool_create_ext_params())
        except Exception as ex:
            self._logger.exception("run_test error {} stopping...".format(ex))
            self._loop.stop()
            return

        self._logger.info("call pregen_reqs")
        await self.pregen_reqs()

        self._logger.info("send ClientReady")
        try:
            self._pipe_conn.send(ClientReady())
        except Exception as e:
            self._logger.exception("Ready send error {}".format(e))
            raise e

    def _on_ClientRun(self, cln_run):
        self._logger.debug("_on_ClientRun _send_mode {}".format(self._send_mode))
        if self._send_mode == LoadClient.SendTime:
            self._loop.call_soon(self.req_send)

    def _on_ClientSend(self, cln_snd):
        self._logger.debug("_on_ClientSend _send_mode {}".format(self._send_mode))
        if self._send_mode == LoadClient.SendSync:
            self.req_send(cln_snd.cnt)

    def read_cb(self):
        force_close = False
        try:
            flag = self._pipe_conn.recv()
            self._logger.debug("read_cb {}".format(flag))
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
            self._logger.exception("Error {}".format(e))
            force_close = True
        if force_close:
            self._loop.create_task(self.stop_test())

    async def gen_signed_req(self):
        self._logger.debug("gen_signed_req")
        if self._closing is True:
            return

        try:
            req_data, req = await self._req_generator.generate_request(self._test_did)
            req = await self.append_taa_acceptance(req)
        except NoReqDataAvailableException:
            self._logger.warning("Cannot generate request since no req data are available.")
            return
        except Exception as e:
            self._logger.exception("generate req error {}".format(e))
            self._loop.stop()
            raise e

        try:
            req_did = self._req_generator.req_did() or self._test_did
            sig_req = await self.ledger_sign_req(self._wallet_handle, req_did, req)
            if sig_req:
                self._stat.signed(req_data)
                self._load_client_reqs.append((req_data, sig_req))
        except Exception as e:
            self._stat.reply(req_data, e)
            self._loop.stop()
            raise e

        await self._req_generator.on_request_generated(req_data, sig_req)

    async def append_taa_acceptance(self, req):
        if self._taa_text == "":
            return req

        if '"type":"10001"' in req:
            return req

        return await ledger.append_txn_author_agreement_acceptance_to_request(
            req, self._taa_text, self._taa_version, None, self.TestAcceptanceMechanism, self._taa_time)

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
                    self._logger.warning("cannot prepare more reqs. Done {}/{}".format(i, self._buff_reqs))
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
            self._logger.exception("stat send error {}".format(e))
            raise e

    def req_send(self, cnt: int = None):
        if self._closing:
            return

        if self._send_mode == LoadClient.SendTime:
            self._loop.call_later(self._batch_rate, self.req_send)

        to_snd = cnt or self._batch_size

        if len(self._load_client_reqs) < to_snd:
            self._logger.warning("Need to send {}, but have {}".format(to_snd, len(self._load_client_reqs)))

        for i in range(min(len(self._load_client_reqs), to_snd)):
            req_data, req = self._load_client_reqs.pop()
            sender = self._loop.create_task(self.submit_req_update(req_data, req))
            sender.add_done_callback(self.done_submit)
            self._send_q.append(sender)

    async def stop_test(self):
        self._logger.info("stop_test...")
        self._closing = True
        if len(self._send_q) > 0:
            await asyncio.gather(*self._send_q, return_exceptions=True)
        if len(self._gen_q) > 0:
            await asyncio.gather(*self._gen_q, return_exceptions=True)
        self._logger.info("stopping queues done")
        try:
            if self._wallet_handle is not None:
                await self.wallet_close(self._wallet_handle)
            self._logger.info("wallet closed")
        except Exception as e:
            self._logger.exception("close_wallet exception: {}".format(e))
        try:
            if self._pool_handle is not None:
                await self.pool_close_pool(self._pool_handle)
            self._logger.info("pool closed")
        except Exception as e:
            self._logger.exception("close_pool_ledger exception: {}".format(e))

        self._loop.call_soon_threadsafe(self._loop.stop)

        self._logger.info("looper stopped")
        dirs_to_dlt = []
        if self._wallet_name is not None and self._wallet_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/wallet"), self._wallet_name))
        if self._pool_name is not None and self._pool_name != "":
            dirs_to_dlt.append(os.path.join(os.path.expanduser("~/.indy_client/pool"), self._pool_name))

        for d in dirs_to_dlt:
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
        self._logger.info("dirs {} deleted".format(dirs_to_dlt))

    @classmethod
    def run(cls, name, genesis_path, pipe_conn, seed, batch_size, batch_rate,
            req_kind, buff_req, wallet_key, pool_config, send_mode, mask_sign,
            taa_text, taa_version, ext_set, log_dir, log_lvl, short_stat):
        if mask_sign:
            logger_init(log_dir, "{}.log".format(name), log_lvl)
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        logging.getLogger(name).info("starting")

        exts = {}
        if ext_set and isinstance(ext_set, str):
            try:
                exts = json.loads(ext_set)
            except Exception as e:
                logging.getLogger(name).warning("{} parse ext settings error {}".format(name, e))
                exts = {}

        cln = cls(name, pipe_conn, batch_size, batch_rate, req_kind, buff_req,
                  pool_config, send_mode, short_stat, **exts)
        try:
            asyncio.run_coroutine_threadsafe(cln.run_test(genesis_path, seed, wallet_key, taa_text, taa_version),
                                             loop=cln._loop)
            cln._loop.run_forever()
        except Exception as e:
            logging.getLogger(name).exception("running error {}".format(e))
        stat = cln._stat.dump_stat(dump_all=True)

        logging.getLogger(name).info("stopped")
        return stat


def update_constraint(constraint, fee_metadata):
    id = constraint.get('constraint_id')
    if id == "ROLE":
        metadata = constraint.get('metadata', {})
        metadata.update(fee_metadata)
        constraint['metadata'] = metadata
    elif id in ["OR", "AND"]:
        for constraint in constraint.get("auth_constraints", []):
            update_constraint(constraint, fee_metadata)
