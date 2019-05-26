#! /usr/bin/env python3

import json
import time
import os
import sys
import asyncio
import argparse
import multiprocessing
import concurrent
import signal
import functools
from datetime import datetime
import yaml
import logging
import shutil

from indy import pool

import perf_load
from perf_load.perf_client_msgs import ClientReady, ClientStop, ClientSend
from perf_load.perf_utils import check_fs, check_seed, logger_init, random_string
from perf_load.perf_gen_req_parser import ReqTypeParser
from perf_load.perf_client import LoadClient
from perf_load.perf_client_runner import ClientRunner
from perf_load.perf_client_fees import LoadClientFees


parser = argparse.ArgumentParser(description='The script generates bunch of txns for the pool with Indy SDK. '
                                 'Detailed description: https://github.com/hyperledger/indy-node/docs/process-based-load-script.md')

parser.add_argument('-c', '--clients', default=0, type=int, required=False, dest='clients',
                    help='Number of client you want to create. '
                         '0 or less means equal to number of available CPUs. '
                         'Default value is 0')

parser.add_argument('-g', '--genesis_path', required=False, dest='genesis_path', type=str,
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis")

parser.add_argument('-s', '--seed', type=check_seed, required=False, dest='seed', action='append',
                    help='Seed to generate submitter did. Default value is Trustee1',
                    default=[])

parser.add_argument('-k', '--req_kind', default="nym", type=str, required=False, dest='req_kind',
                    help='Supported requests {} Default value is "nym". Could be combined in form of'
                         ' JSON array or JSON obj'.format(ReqTypeParser.supported_requests()))

parser.add_argument('-n', '--batch_size', default=10, type=int, required=False, dest='batch_size',
                    help='Number of transactions to submit in one batch. Default value is 10')

parser.add_argument('-r', '--refresh_rate', default=10, type=float, required=False, dest='refresh_rate',
                    help='Statistics refresh rate in sec. Default value is 10')

parser.add_argument('-b', '--buff_req', default=30, type=int, required=False, dest='buff_req',
                    help='Number of pregenerated reqs before start. Default value is 30')

parser.add_argument('-d', '--out_dir', default=".", required=False, dest='out_dir', type=str,
                    help='Directory to save output files. Default value is "."')

parser.add_argument('--val_sep', default="|", type=str, required=False, dest='val_sep',
                    help='csv file separator. Default value is "|"')

parser.add_argument('-w', '--wallet_key', default="key", type=str, required=False, dest='wallet_key',
                    help='Wallet encryption key. Default value is "key"')

parser.add_argument('-m', '--mode', default="p", choices=['p', 't'], required=False, dest='mode',
                    help='Whether to create clients via processes or threads. Default "p"')

parser.add_argument('-p', '--pool_config', default="", type=str, required=False, dest='pool_config',
                    help='Configuration of pool as JSON. The value will be passed to open_pool call. Default value is empty')

parser.add_argument('-y', '--sync_mode', default="freeflow", choices=['freeflow', 'all', 'one', 'wait_resp'],
                    required=False, dest='sync_mode',
                    help='Client sync mode. Default value is freeflow')

parser.add_argument('-l', '--load_rate', default=10, type=float, required=False, dest='load_rate',
                    help='Batches per sec. Default value is 10')

parser.add_argument('-o', '--out_file', default="", type=str, required=False, dest='out_file',
                    help='Output file. Default value is stdout')

parser.add_argument('--load_time', default=0, type=float, required=False, dest='load_time',
                    help='Work no longer then load_time sec. Default value is 0')

parser.add_argument('--ext_set', default=None, type=str, required=False, dest='ext_set',
                    help='Ext settings to use')

parser.add_argument('--log_lvl', default=logging.INFO, type=int, required=False, dest='log_lvl',
                    help='Logging level')

parser.add_argument('--short_stat', action='store_true', dest='short_stat', help='Store only total statistics')

parser.add_argument('--test_conn', action='store_true', dest='test_conn',
                    help='Check pool connection with provided genesis file')

parser.add_argument('--taa_text', default="test transaction author agreement text", type=str, required=False,
                    help='Transaction author agreement text')

parser.add_argument('--taa_version', default="test_taa", type=str, required=False,
                    help='Transaction author agreement version')


class LoadRunner:
    def __init__(self, clients=0, genesis_path="~/.indy-cli/networks/sandbox/pool_transactions_genesis",
                 seed=["000000000000000000000000Trustee1"], req_kind="nym", batch_size=10, refresh_rate=10,
                 buff_req=30, out_dir=".", val_sep="|", wallet_key="key", mode="p", pool_config='',
                 sync_mode="freeflow", load_rate=10, out_file="", load_time=0, taa_text="", taa_version="",
                 ext_set=None, client_runner=LoadClient.run, log_lvl=logging.INFO,
                 short_stat=False):
        self._client_runner = client_runner
        self._clients = dict()  # key process future; value ClientRunner
        self._loop = asyncio.get_event_loop()
        self._out_dir = out_dir
        self._succ_f = None
        self._failed_f = None
        self._total_f = None
        self._nacked_f = None
        self._start_counter = time.perf_counter()
        self._proc_count = clients if clients > 0 else multiprocessing.cpu_count()
        self._refresh_rate = refresh_rate if refresh_rate > 0 else 10
        self._buff_req = buff_req if buff_req >= 0 else 30
        self._value_separator = val_sep if val_sep != "" else "|"
        self._batch_size = batch_size if batch_size > 0 else 10
        self._stop_sec = load_time if load_time > 0 else 0
        self._genesis_path = genesis_path
        self._seed = seed
        self._req_kind = req_kind
        self._wallet_key = wallet_key
        self._sync_mode = sync_mode
        self._start_sync = sync_mode in ['all', 'one']
        self._mode = mode
        self._pool_config = None
        lr = load_rate if load_rate > 0 else 10
        self._batch_rate = 1 / lr
        self._taa_text = taa_text
        self._taa_version = taa_version
        self._ext_set = ext_set
        if pool_config:
            try:
                self._pool_config = json.loads(pool_config)
            except Exception as ex:
                raise RuntimeError("pool_config param is ill-formed JSON: {}".format(ex))

        self._log_lvl = log_lvl
        self._logger = logging.getLogger(__name__)
        self._out_file = self.prepare_fs(out_file)
        self._short_stat = short_stat

    def process_reqs(self, stat, name: str = ""):
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f
        self._logger.debug("process_reqs stat {}, name {}".format(stat, name))
        if not isinstance(stat, dict):
            return
        reqs = stat.get("reqs", [])
        tot = []
        suc = []
        nack = []
        fails = []
        for (r_id, r_data) in reqs:
            # ["client", "label", "id", "status", "client_preparing", "client_prepared", "client_sent", "client_reply", "server_reply"]
            self._logger.debug("process_reqs r_id {}, r_data {}".format(r_id, r_data))
            status = r_data.get("status", "")
            tot.append(self._value_separator.join(
                [name, r_data.get("label", ""), str(r_id), status,
                 str(r_data.get("client_preparing", 0)), str(r_data.get("client_prepared", 0)),
                 str(r_data.get("client_signed", 0)), str(r_data.get("client_sent", 0)),
                 str(r_data.get("client_reply", 0)), str(r_data.get("server_reply", 0))]))

            # ["id", "req", "resp"]
            val = self._value_separator.join([str(r_id), r_data.get("req", ""), str(r_data.get("resp", ""))])
            if status == "succ":
                suc.append(val)
            elif status in ["nack", "reject"]:
                nack.append(val)
            else:
                fails.append(val)

        if tot:
            self._total_f.write("\n".join(tot + [""]))

        if self._short_stat:
            return

        if suc:
            self._succ_f.write("\n".join(suc + [""]))
        if nack:
            self._nacked_f.write("\n".join(nack + [""]))
        if fails:
            self._failed_f.write("\n".join(fails + [""]))

    def sig_handler(self, sig):
        self._logger.debug("sig_handler sig {}".format(sig))
        for prc, cln in self._clients.items():
            self._logger.debug("sig_handler prc {} cln {}".format(prc, cln))
            try:
                if not cln.is_finished() and cln.conn:
                    cln.conn.send(ClientStop())
                if sig == signal.SIGTERM:
                    prc.cancel()
            except Exception as e:
                self._logger.exception("Sent stop to client {} error {}".format(cln.name, e))

    def _tick_all(self):
        self._logger.debug("_tick_all")
        self._loop.call_later(self._batch_rate, self._tick_all)
        for cln in self._clients.values():
            self._logger.debug("_tick_all cln {}".format(cln))
            try:
                if cln.status == ClientRunner.ClientRun and cln.conn:
                    cln.conn.send(ClientSend(self._batch_size))
            except Exception as e:
                self._logger.exception("Sent stop to client {} error {}".format(cln.name, e))

    def _tick_one(self, idx: int = 0):
        i = idx % len(self._clients)
        self._logger.debug("_tick_one idx {} i {}".format(idx, i))
        self._loop.call_later(self._batch_rate, self._tick_one, i + 1)
        key = list(self._clients)[i]
        cln = self._clients[key]
        self._logger.debug("_tick_one cln {}".format(cln))
        try:
            if cln.status == ClientRunner.ClientRun and cln.conn:
                cln.conn.send(ClientSend(self._batch_size))
        except Exception as e:
            self._logger.exception("Sent stop to client {} error {}".format(cln.name, e))

    def start_clients(self):
        to_start = [c for c in self._clients.values() if c.status == ClientRunner.ClientReady]
        self._logger.debug("start_clients to_start {} _start_sync {} _sync_mode {}".
                           format(to_start, self._start_sync, self._sync_mode))
        if self._start_sync and len(to_start) != len(self._clients):
            return
        for cln in to_start:
            cln.run_client()

        all_run = all([c.status == ClientRunner.ClientRun for c in self._clients.values()])
        if all_run and self._sync_mode == 'all':
            self._tick_all()
        elif all_run and self._sync_mode == 'one':
            self._tick_one(0)

        self.schedule_stop()

    def request_stat(self):
        self._logger.debug("request_stat")
        for cln in self._clients.values():
            cln.req_stats()

    def read_client_cb(self, prc):
        self._logger.debug("read_client_cb prc {}".format(prc))
        try:
            r_data = self._clients[prc].conn.recv()
            self._logger.debug("read_client_cb r_data {}".format(r_data))
            if isinstance(r_data, dict):
                self._clients[prc].refresh_stat(r_data)
                self.process_reqs(r_data, self._clients[prc].name)
            elif isinstance(r_data, ClientReady):
                self._clients[prc].status = ClientRunner.ClientReady
                self.start_clients()
            else:
                self._logger.warning("Recv garbage {} from {}".format(r_data, self._clients[prc].name))
        except Exception as e:
            self._logger.exception("{} read_client_cb error {}".format(self._clients[prc].name, e))

    def client_done(self, client):
        self._logger.debug("client_done client {}".format(client))
        try:
            last_stat = client.result()
            self._logger.debug("client_done last_stat {}".format(last_stat))
            self._clients[client].refresh_stat(last_stat)
            self.process_reqs(last_stat, self._clients[client].name)
        except Exception as e:
            self._logger.exception("Client Error {}".format(e))

        self._clients[client].stop_client()
        self._loop.remove_reader(self._clients[client].conn)

        is_closing = all([cln.is_finished() for cln in self._clients.values()])

        if is_closing:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def get_refresh_str(self):
        self._logger.debug("get_refresh_str")
        clients = 0
        total_sent = 0
        total_succ = 0
        total_failed = 0
        total_nack = 0
        total_reject = 0

        for cln in self._clients.values():
            if cln.status == ClientRunner.ClientRun:
                clients += 1
            total_sent += cln.total_sent
            total_succ += cln.total_succ
            total_failed += cln.total_failed
            total_nack += cln.total_nack
            total_reject += cln.total_reject
        print_str = "Time {:.2f} Clients {}/{} Sent: {} Succ: {} Failed: {} Nacked: {} Rejected: {}".format(
            time.perf_counter() - self._start_counter, clients, len(self._clients),
            total_sent, total_succ, total_failed, total_nack, total_reject)
        return print_str

    def prepare_fs(self, out_file):
        self._logger.debug("prepare_fs out_dir {}, out_file {}".
                           format(self._out_dir, out_file))

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
        print("client", "label", "id", "status", "client_preparing", "client_prepared",
              "client_signed", "client_sent", "client_reply", "server_reply",
              file=self._total_f, sep=self._value_separator)

        ret_out = sys.stdout
        if out_file:
            ret_out = open(os.path.join(self._out_dir, out_file), "w")
        return ret_out

    def close_fs(self):
        self._logger.debug("close_fs")
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f
        self._failed_f.close()
        self._total_f.close()
        self._succ_f.close()
        self._nacked_f.close()
        if self._out_file != sys.stdout:
            self._out_file.close()

    def screen_stat(self):
        self._logger.debug("close_fs")
        ends = "\n" if self._out_file != sys.stdout else "\r"
        print(self.get_refresh_str(), end=ends, file=self._out_file)
        self.request_stat()
        self._total_f.flush()
        self._failed_f.flush()
        self._succ_f.flush()
        self._nacked_f.flush()
        if self._out_file != sys.stdout:
            self._out_file.flush()
        self._loop.call_later(self._refresh_rate, self.screen_stat)

    def schedule_stop(self):
        self._logger.debug("schedule_stop _stop_sec".format(self._stop_sec))
        if self._stop_sec > 0:
            self._loop.call_later(self._stop_sec, self.sig_handler, signal.SIGINT)

    def load_run(self):
        print("Version                  ", perf_load.__version__, file=self._out_file)
        print("Number of client         ", self._proc_count, file=self._out_file)
        print("Path to genesis txns file", self._genesis_path, file=self._out_file)
        print("Seed                     ", self._seed, file=self._out_file)
        print("Batch size               ", self._batch_size, file=self._out_file)
        print("Request kind             ", self._req_kind, file=self._out_file)
        print("Refresh rate, sec        ", self._refresh_rate, file=self._out_file)
        print("Pregenerated reqs cnt    ", self._buff_req, file=self._out_file)
        print("Output directory         ", self._out_dir, file=self._out_file)
        print("Value Separator          ", self._value_separator, file=self._out_file)
        print("Wallet Key               ", self._wallet_key, file=self._out_file)
        print("Started At               ", datetime.now(), file=self._out_file)
        print("Mode                     ", "processes" if self._mode == 'p' else "threads", file=self._out_file)
        print("Sync mode                ", self._sync_mode, file=self._out_file)
        print("Pool config              ", self._pool_config, file=self._out_file)
        print("Load rate batches per sec", 1 / self._batch_rate, file=self._out_file)
        print("Ext settings             ", self._ext_set, file=self._out_file)
        print("Save short statistics    ", self._short_stat, file=self._out_file)

        load_client_mode = LoadClient.SendTime
        if self._sync_mode in ['all', 'one']:
            load_client_mode = LoadClient.SendSync
        elif self._sync_mode == 'wait_resp':
            load_client_mode = LoadClient.SendResp
            self._batch_size = 1
            self._buff_req = 0

        self._logger.info("load_run version {} params {}".format(perf_load.__version__, self.__dict__))

        self._loop.add_signal_handler(signal.SIGTERM, functools.partial(self.sig_handler, signal.SIGTERM))
        self._loop.add_signal_handler(signal.SIGINT, functools.partial(self.sig_handler, signal.SIGINT))

        if self._mode == 'p':
            executor = concurrent.futures.ProcessPoolExecutor(self._proc_count)
        else:
            executor = concurrent.futures.ThreadPoolExecutor(self._proc_count)
        for i in range(self._proc_count):
            rd, wr = multiprocessing.Pipe()
            prc_name = "LoadClient_{}".format(i)
            prc = executor.submit(self._client_runner, prc_name, self._genesis_path, wr, self._seed, self._batch_size,
                                  self._batch_rate, self._req_kind, self._buff_req, self._wallet_key, self._pool_config,
                                  load_client_mode, self._mode == 'p', self._taa_text, self._taa_version, self._ext_set,
                                  self._out_dir, self._log_lvl, self._short_stat)
            prc.add_done_callback(self.client_done)
            self._loop.add_reader(rd, self.read_client_cb, prc)
            self._clients[prc] = ClientRunner(prc_name, rd, self._out_file)
            self._logger.info("load_run client {} created".format(prc_name))

        self.screen_stat()

        self._logger.info("load_run all clients created")
        self._loop.run_forever()

        self._logger.info("load_run stopping...")
        self._loop.remove_signal_handler(signal.SIGTERM)
        self._loop.remove_signal_handler(signal.SIGINT)

        print("", file=self._out_file)
        print("DONE At", datetime.now(), file=self._out_file)
        print(self.get_refresh_str(), file=self._out_file)
        self.close_fs()
        self._logger.info("load_run stopped")


def check_genesis(gen_path):
    loop = asyncio.get_event_loop()
    pool_cfg = json.dumps({"genesis_txn": gen_path})
    pool_name = "pool_{}".format(random_string(24))
    loop.run_until_complete(pool.set_protocol_version(2))
    try:
        loop.run_until_complete(pool.create_pool_ledger_config(pool_name, pool_cfg))
        pool_handle = loop.run_until_complete(pool.open_pool_ledger(pool_name, None))
    except Exception as ex:
        raise argparse.ArgumentTypeError(ex)

    loop.run_until_complete(pool.close_pool_ledger(pool_handle))
    dir_to_dlt = os.path.join(os.path.expanduser("~/.indy_client/pool"), pool_name)
    if os.path.isdir(dir_to_dlt):
        shutil.rmtree(dir_to_dlt, ignore_errors=True)


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    args, extra = parser.parse_known_args()
    dict_args = vars(args)

    if len(extra) > 1:
        raise argparse.ArgumentTypeError("Only path to config file expected, but found extra arguments: {}".format(extra))

    conf_vals = {}
    try:
        if extra:
            with open(extra[0], "r") as conf_file:
                conf_vals = yaml.load(conf_file)
    except Exception as ex:
        print("Config parse error", ex)
        conf_vals = {}

    dict_args.update(conf_vals)

    if not dict_args["seed"]:
        dict_args["seed"].append("000000000000000000000000Trustee1")

    dict_args["genesis_path"] = check_fs(False, dict_args["genesis_path"])
    dict_args["out_dir"] = check_fs(True, dict_args["out_dir"])

    # Prepare output directory
    out_dir = dict_args["out_dir"]
    test_name = "load_test_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    out_dir = os.path.expanduser(os.path.join(out_dir, test_name))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Initialize logger
    log_lvl = dict_args["log_lvl"]
    logger_init(out_dir, "{}.log".format(test_name), log_lvl)

    check_genesis(dict_args["genesis_path"])

    if dict_args["test_conn"]:
        exit(0)

    tr = LoadRunner(dict_args["clients"], dict_args["genesis_path"], dict_args["seed"], dict_args["req_kind"],
                    dict_args["batch_size"], dict_args["refresh_rate"], dict_args["buff_req"], out_dir,
                    dict_args["val_sep"], dict_args["wallet_key"], dict_args["mode"], dict_args["pool_config"],
                    dict_args["sync_mode"], dict_args["load_rate"], dict_args["out_file"], dict_args["load_time"],
                    dict_args["taa_text"], dict_args["taa_version"], dict_args["ext_set"],
                    client_runner=LoadClient.run if not dict_args["ext_set"] else LoadClientFees.run,
                    log_lvl=log_lvl, short_stat=dict_args["short_stat"])
    tr.load_run()
