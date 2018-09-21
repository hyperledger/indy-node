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

from perf_load.perf_client_msgs import ClientReady, ClientStop, ClientSend, ClientMsg
from perf_load.perf_utils import check_fs, check_seed
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

parser.add_argument('-g', '--genesis', required=False, dest='genesis_path', type=functools.partial(check_fs, False),
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis")

parser.add_argument('-s', '--seed', type=check_seed, required=False, dest='seed',
                    help='Seed to generate submitter did. Default value is Trustee1',
                    default="000000000000000000000000Trustee1")

parser.add_argument('-k', '--kind', default="nym", type=str, required=False, dest='req_kind',
                    help='Supported requests {} Default value is "nym". Could be combined in form of'
                         ' JSON array or JSON obj'.format(ReqTypeParser.supported_requests()))

parser.add_argument('-n', '--num', default=10, type=int, required=False, dest='batch_size',
                    help='Number of transactions to submit in one batch. Default value is 10')

parser.add_argument('-r', '--refresh', default=10, type=float, required=False, dest='refresh_rate',
                    help='Statistics refresh rate in sec. Default value is 10')

parser.add_argument('-b', '--buff_req', default=30, type=int, required=False, dest='buff_req',
                    help='Number of pregenerated reqs before start. Default value is 30')

parser.add_argument('-d', '--directory', default=".", required=False, dest='out_dir',
                    type=functools.partial(check_fs, True),
                    help='Directory to save output files. Default value is "."')

parser.add_argument('--sep', default="|", type=str, required=False, dest='val_sep',
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

parser.add_argument('-o', '--out', default="", type=str, required=False, dest='out_file',
                    help='Output file. Default value is stdout')

parser.add_argument('--load_time', default=0, type=float, required=False, dest='load_time',
                    help='Work no longer then load_time sec. Default value is 0')

parser.add_argument('--ext', default=None, type=str, required=False, dest='ext_set',
                    help='Ext settings to use')


class LoadRunner:
    def __init__(self, clients=0, genesis_path="~/.indy-cli/networks/sandbox/pool_transactions_genesis",
                 seed="000000000000000000000000Trustee1", req_kind="nym", batch_size=10, refresh_rate=10,
                 buff_req=30, out_dir=".", val_sep="|", wallet_key="key", mode="p", pool_config='',
                 sync_mode="freeflow", load_rate=10, out_file="", load_time=0, ext_set=None,
                 client_runner=LoadClient.run):
        self._client_runner = client_runner
        self._clients = dict()  # key process future; value ClientRunner
        self._loop = asyncio.get_event_loop()
        self._out_dir = ""
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
        self._ext_set = ext_set
        if pool_config:
            try:
                self._pool_config = json.loads(pool_config)
            except Exception as ex:
                raise RuntimeError("pool_config param is ill-formed JSON: {}".format(ex))

        self._out_file = self.prepare_fs(out_dir, "load_test_{}".
                                         format(datetime.now().strftime("%Y%m%d_%H%M%S")), out_file)

    def process_reqs(self, stat, name: str = ""):
        assert self._failed_f
        assert self._total_f
        assert self._succ_f
        assert self._nacked_f
        if not isinstance(stat, dict):
            return
        reqs = stat.get("reqs", [])
        tot = []
        suc = []
        nack = []
        fails = []
        for (r_id, r_data) in reqs:
            # ["client", "label", "id", "status", "client_preparing", "client_prepared", "client_sent", "client_reply", "server_reply"]
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
        if suc:
            self._succ_f.write("\n".join(suc + [""]))
        if nack:
            self._nacked_f.write("\n".join(nack + [""]))
        if fails:
            self._failed_f.write("\n".join(fails + [""]))

    def sig_handler(self, sig):
        for prc, cln in self._clients.items():
            try:
                if not cln.is_finished() and cln.conn:
                    cln.conn.send(ClientStop())
                if sig == signal.SIGTERM:
                    prc.cancel()
            except Exception as e:
                print("Sent stop to client {} error {}".format(cln.name, e), file=self._out_file)

    def _tick_all(self):
        self._loop.call_later(self._batch_rate, self._tick_all)
        for cln in self._clients.values():
            try:
                if cln.status == ClientRunner.ClientRun and cln.conn:
                    cln.conn.send(ClientSend(self._batch_size))
            except Exception as e:
                print("Sent stop to client {} error {}".format(cln.name, e), file=self._out_file)

    def _tick_one(self, idx: int = 0):
        i = idx % len(self._clients)
        self._loop.call_later(self._batch_rate, self._tick_one, i + 1)
        key = list(self._clients)[i]
        cln = self._clients[key]
        try:
            if cln.status == ClientRunner.ClientRun and cln.conn:
                cln.conn.send(ClientSend(self._batch_size))
        except Exception as e:
            print("Sent stop to client {} error {}".format(cln.name, e), file=self._out_file)

    def start_clients(self):
        to_start = [c for c in self._clients.values() if c.status == ClientRunner.ClientReady]
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
        for cln in self._clients.values():
            cln.req_stats()

    def read_client_cb(self, prc):
        try:
            r_data = self._clients[prc].conn.recv()
            if isinstance(r_data, dict):
                self._clients[prc].refresh_stat(r_data)
                self.process_reqs(r_data, self._clients[prc].name)
            elif isinstance(r_data, ClientReady):
                self._clients[prc].status = ClientRunner.ClientReady
                self.start_clients()
            elif isinstance(r_data, ClientMsg):
                print("{} : {}".format(self._clients[prc].name, r_data.msg), file=self._out_file)
            else:
                print("Recv garbage {} from {}".format(r_data, self._clients[prc].name), file=self._out_file)
        except Exception as e:
            print("{} read_client_cb error {}".format(self._clients[prc].name, e), file=self._out_file)
            # self._clients[prc].conn = None

    def client_done(self, client):
        try:
            last_stat = client.result()
            self._clients[client].refresh_stat(last_stat)
            self.process_reqs(last_stat, self._clients[client].name)
        except Exception as e:
            print("Client Error", e, file=self._out_file)

        self._clients[client].stop_client()
        self._loop.remove_reader(self._clients[client].conn)

        is_closing = all([cln.is_finished() for cln in self._clients.values()])

        if is_closing:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def get_refresh_str(self):
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

    def prepare_fs(self, out_dir, test_dir_name, out_file):
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
        print("client", "label", "id", "status", "client_preparing", "client_prepared",
              "client_signed", "client_sent", "client_reply", "server_reply",
              file=self._total_f, sep=self._value_separator)

        ret_out = sys.stdout
        if out_file:
            ret_out = open(os.path.join(self._out_dir, out_file), "w")
        return ret_out

    def close_fs(self):
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
        if self._stop_sec > 0:
            self._loop.call_later(self._stop_sec, self.sig_handler, signal.SIGINT)

    def load_run(self):
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

        load_client_mode = LoadClient.SendTime
        if self._sync_mode in ['all', 'one']:
            load_client_mode = LoadClient.SendSync
        elif self._sync_mode == 'wait_resp':
            load_client_mode = LoadClient.SendResp
            self._batch_size = 1
            self._buff_req = 0

        print("load_client_mode", load_client_mode, file=self._out_file)

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
                                  load_client_mode, self._mode == 'p')
            prc.add_done_callback(self.client_done)
            self._loop.add_reader(rd, self.read_client_cb, prc)
            self._clients[prc] = ClientRunner(prc_name, rd, self._out_file)

        self.screen_stat()

        self._loop.run_forever()

        self._loop.remove_signal_handler(signal.SIGTERM)
        self._loop.remove_signal_handler(signal.SIGINT)

        print("", file=self._out_file)
        print("DONE At", datetime.now(), file=self._out_file)
        print(self.get_refresh_str(), file=self._out_file)
        self.close_fs()


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    args = parser.parse_args()
    tr = LoadRunner(args.clients, args.genesis_path, args.seed, args.req_kind, args.batch_size, args.refresh_rate,
                    args.buff_req, args.out_dir, args.val_sep, args.wallet_key, args.mode, args.pool_config,
                    args.sync_mode, args.load_rate, args.out_file, args.load_time, args.ext_set,
                    client_runner=LoadClient.run if not args.ext_set else LoadClientFees.run)
    tr.load_run()
