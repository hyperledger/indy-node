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

from indy import pool, wallet, did, ledger


parser = argparse.ArgumentParser(description='The script generates bunch of txns for the pool with Indy SDK.')

parser.add_argument('-c', '--clients',
                    help='Number of client you want to create. Each client is a separate process.'
                         '0 or less means equal to number of available CPUs'
                         'Default value is 0',
                    default=0, type=int, required=False, dest='clients')


def check_fs(is_dir: bool, fs_name: str):
    pp = os.path.expanduser(fs_name)
    rights = os.W_OK if is_dir else os.R_OK
    chk_func = os.path.isdir if is_dir else os.path.isfile
    if chk_func(pp) and os.access(pp, rights):
        return pp
    raise argparse.ArgumentTypeError("{} not found or access error".format(pp))


parser.add_argument('-g', '--genesis',
                    help='Path to genesis txns file'
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis",
                    type=functools.partial(check_fs, False), required=False,
                    dest='genesis_path')


def check_seed(seed: str):
    if len(seed) == 32:
        return seed
    raise argparse.ArgumentTypeError("Seed must be 32 characters long but provided {}".format(len(seed)))


parser.add_argument('-s', '--seed',
                    help='Seed to generate submitter did'
                         'Default value is Trustee1',
                    default="000000000000000000000000Trustee1",
                    type=check_seed, required=False, dest='seed')

parser.add_argument('-k', '--kind',
                    help='Kind of request kind to use. One of ["nym", "schema", "attribute", "claim", "rand"]'
                         'Default value is "nym"',
                    default="nym", choices=['nym', 'schema', 'attribute', 'claim', 'rand'],
                    required=False, dest='req_kind')

parser.add_argument('-n', '--num',
                    help='How many transactions to submit.'
                         'Default value is 100',
                    default=100, type=int, required=False, dest='batch_size')

parser.add_argument('-t', '--timeout',
                    help='Timeout between batches.'
                         'Default value is 0 - send once and finish',
                    default=0, type=float, required=False, dest='batch_timeout')

parser.add_argument('-r', '--refresh',
                    help='Number of replied txns to refresh statistics.'
                         'Default value is 100',
                    default=100, type=int, required=False, dest='refresh_rate')

parser.add_argument('-b', '--bg_tasks',
                    help='Number of background tasks per process, sending and generating.'
                         'Default value is 30',
                    default=30, type=int, required=False, dest='bg_tasks')

parser.add_argument('-d', '--directory',
                    help='Directory to save output files'
                         'Default value is "."',
                    default=".", type=functools.partial(check_fs, True), required=False, dest='out_dir')

parser.add_argument('--sep',
                    help='Value separator used in result file'
                         'Default value is "|"',
                    default="|", type=str, required=False, dest='val_sep')


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

        self._reqs = dict()

    def preparing(self, req_id):
        self._reqs.setdefault(req_id, dict())["client_preparing"] = time.time()

    def prepared(self, req_id):
        self._reqs.setdefault(req_id, dict())["client_prepared"] = time.time()
        self._req_prep += 1

    def sent(self, req_id, req):
        self._reqs.setdefault(req_id, dict())["client_sent"] = time.time()
        self._reqs[req_id]["req"] = req
        self._req_sent += 1

    def reply(self, req_id, reply_or_exception):
        self._reqs.setdefault(req_id, dict())["client_reply"] = time.time()
        resp = reply_or_exception
        if isinstance(reply_or_exception, str):
            try:
                resp = json.loads(reply_or_exception)
            except Exception as e:
                print("Cannot parse response", e)
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
                server_time = int(resp['result']['txnTime'])
                self._reqs[req_id]["server_reply"] = server_time
                self._server_min_txn_time = min(self._server_min_txn_time, server_time)
                self._server_max_txn_time = max(self._server_max_txn_time, server_time)
            else:
                self._req_fail += 1
                status = "fail"
        else:
            self._req_fail += 1
            status = "fail"
        self._reqs[req_id]["status"] = status
        self._reqs[req_id]["resp"] = resp

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
        reqs = [k for k, v in self._reqs.items() if "status" in v or dump_all]
        for r in reqs:
            ret_val["reqs"].append((r, self._reqs.pop(r)))
        return ret_val


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
        self._reqs = []
        self._loop.add_reader(self._pipe_conn, self.read_cb)
        self._closing = False
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout
        self._gen_q = []
        self._send_q = []
        self._req_generator = self.get_builder(req_kind)
        assert self._req_generator is not None
        self._bg_send_last = 0
        self._sent_in_batch = None

    async def run_test(self, genesis_path, seed):
        pool_cfg = json.dumps({"genesis_txn": genesis_path})
        await pool.create_pool_ledger_config(self._pool_name, pool_cfg)
        self._pool_handle = await pool.open_pool_ledger(self._pool_name, None)
        self._wallet_name = "{}_wallet".format(self._pool_name)
        await wallet.create_wallet(self._pool_name, self._wallet_name, None, None, None)
        self._wallet_handle = await wallet.open_wallet(self._wallet_name, None, None)
        self._test_did, self._test_verk = await did.create_and_store_my_did(self._wallet_handle, json.dumps({'seed': seed}))

        self.gen_reqs()

    def get_builder(self, req_kind):
        if req_kind == 'nym':
            return self.gen_signed_nym
        if req_kind == 'rand':
            return self.gen_signed_nym
        return self.gen_signed_nym

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

    # Copied from Plenum
    def random_string(self, sz: int) -> str:
        assert (sz > 0), "Expected random string size cannot be less than 1"
        rv = libnacl.randombytes(sz // 2).hex()
        return rv if sz % 2 == 0 else rv + hex(libnacl.randombytes_uniform(15))[-1]

    # Copied from Plenum
    def rawToFriendly(self, raw):
        return base58.b58encode(raw).decode("utf-8")

    async def gen_signed_nym(self):
        # print("gen_signed_nym")
        if self._closing is True:
            return

        raw = libnacl.randombytes(16)
        did = self.rawToFriendly(raw)

        self._stat.preparing(did)
        try:
            req = await ledger.build_nym_request(self._test_did, did, None, None, None)
            sig_req = await ledger.sign_request(self._wallet_handle, self._test_did, req)
            self._reqs.append((did, sig_req))
            self._stat.prepared(did)
        except Exception as e:
            self._stat.reply(did, e)
            print("{} prepare req error {}".format(self._name, e))

    def watch_queues(self):
        if len(self._reqs) + len(self._gen_q) < self._batch_size:
            self._loop.call_soon(self.gen_reqs)

        if len(self._reqs) > 0 and len(self._send_q) < self._send_lim:
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
        if avail_gens <= 0 or len(self._gen_q) + len(self._reqs) > self.max_in_bg():
            return

        for i in range(0, min(avail_gens, self._batch_size)):
            try:
                builder = self._loop.create_task(self._req_generator())
                builder.add_done_callback(self.check_batch_avail)
                self._gen_q.append(builder)
            except Exception as e:
                print("{} generate req error {}".format(self._name, e))

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
        if self._stat._req_sent % self._refresh == 0:
            self._loop.call_soon(self.send_stat)

    def send_stat(self):
        st = self._stat.dump_stat()
        try:
            self._pipe_conn.send(st)
        except Exception as e:
            print("{} stat send error {}".format(self._name, e))

    def req_send(self):
        if self._closing:
            return

        avail_sndrs = self._send_lim - len(self._send_q)
        if avail_sndrs <= 0:
            return

        if self._sent_in_batch is None:  # should wait for a timeout
            time_spent = time.perf_counter() - self._bg_send_last
            if time_spent >= self._batch_timeout:
                self._sent_in_batch = 0
            else:
                return

        to_snd = None
        if 0 <= self._sent_in_batch < self._batch_size:
            to_snd = min(len(self._reqs), avail_sndrs, (self._batch_size - self._sent_in_batch))
            for i in range(0, to_snd):
                req_id, req = self._reqs.pop()
                try:
                    sender = self._loop.create_task(self.submit_req_update(req_id, req))
                    sender.add_done_callback(self.done_submit)
                    self._send_q.append(sender)
                except Exception as e:
                    print("{} submit err {}".format(self._name, e))
                self._sent_in_batch += 1

        if self._sent_in_batch >= self._batch_size:
            self._sent_in_batch = None
            self._bg_send_last = time.perf_counter()
            if self._batch_timeout == 0:
                self._loop.create_task(self.stop_test())
            else:
                self._loop.call_later(self._batch_timeout, self.req_send)

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


def run_client(name, genesis_path, pipe_conn, seed, batch_size, batch_timeout, req_kind, bg_tasks, refresh):
    cln = LoadClient(name, pipe_conn, batch_size, batch_timeout, req_kind, bg_tasks, refresh)
    try:
        asyncio.run_coroutine_threadsafe(cln.run_test(genesis_path, seed), loop=cln._loop)
        cln._loop.run_forever()
    except Exception as e:
        print("{} running error {}".format(cln._name, e))
    # cln._loop.close()
    stat = cln._stat.dump_stat(dump_all=True)
    return stat


class ClientRunner:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn
        self.closed = False

        self.last_refresh = 0

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
        self.last_refresh = time.perf_counter()
        self.total_sent = stat.get("total_sent", self.total_sent)
        self.total_succ = stat.get("total_succ", self.total_succ)
        self.total_failed = stat.get("total_fail", self.total_failed)
        self.total_nack = stat.get("total_nacked", self.total_nack)
        self.total_reject = stat.get("total_rejected", self.total_reject)
        self.total_server_time = stat.get("server_time", self.total_server_time)


class TestRunner:
    def __init__(self):
        self._clients = dict()  # key pocess future; value ClientRunner
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
            # ["id", "status", "client_preparing", "client_prepared", "client_sent", "client_reply", "server_reply"]
            status = r_data.get("status", "")
            print(r_id, status, r_data.get("client_preparing", 0), r_data.get("client_prepared", 0),
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
        print("id", "status", "client_preparing", "client_prepared", "client_sent", "client_reply", "server_reply",
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
        bg_tasks = args.bg_tasks if args.bg_tasks > 0 else 300
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
                                  args.req_kind, bg_tasks, refresh)
            prc.add_done_callback(self.client_done)
            self._loop.add_reader(rd, self.read_client_cb, prc)
            self._clients[prc] = ClientRunner(prc_name, rd)

        print("Started", proc_count, "processes")

        self._loop.run_forever()

        self._loop.remove_signal_handler(signal.SIGTERM)
        self._loop.remove_signal_handler(signal.SIGINT)

        print("")
        print("DONE")
        print(self.get_refresh_str())
        self.close_fs()


if __name__ == '__main__':
    args = parser.parse_args()
    tr = TestRunner()
    tr.test_run(args)
