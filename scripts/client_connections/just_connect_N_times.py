import argparse
import json
import multiprocessing
import time
import asyncio

from multiprocessing import Process

import os

import functools

import sys
from indy import pool

count_of_connected = 0
count_of_not_connected = 0


def run_client(genesis_path, pipe_conn, client_number):

    async def run_test(genesis_path, loop, pipe_conn):
        try:
            pool_cfg = json.dumps({"genesis_txn": genesis_path})

            # TODO: remove after latest changes committed
            pool_name = "pool_{}_{}".format(int(time.time()), os.getpid())
            await pool.set_protocol_version(2)

            await pool.create_pool_ledger_config(pool_name, pool_cfg)
            await pool.open_pool_ledger(pool_name, None)
            pipe_conn.send((0, client_number))
            time.sleep(100000)
        except Exception:
            pipe_conn.send((1, client_number))
            loop.call_soon(loop.stop)
            return

    async def periodically_print():
        while True:
            print("Client with number: {}. Trying to connect ....".format(client_number))
            await asyncio.sleep(5)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(
            periodically_print(),
            run_test(genesis_path, loop, pipe_conn)
        ))
    except Exception as e:
        pipe_conn.send(e)


def read_cb(pipe_conn):
    global count_of_connected
    global count_of_not_connected
    res = pipe_conn.recv()
    if isinstance(res, tuple):
        code, cl_number = res
        if code == 0:
            print("Client with number {} is connected".format(cl_number))
            count_of_connected += 1
        elif code == 1:
            print("Client with number {} is not connected".format(cl_number))
            count_of_not_connected += 1
        print("Count of connected clients: {}".format(count_of_connected))
        print("Count of not connected clients: {}".format(count_of_not_connected))
    else:
        print(res)


async def start_all_procs(args, wr):
    processes = []
    for client_number in range(args.clients):
        process = Process(target=run_client, args=(args.genesis_path, wr, client_number))
        processes.append(process)
        process.start()


parser = argparse.ArgumentParser(description="Create N simultaneous connection to pool ")
parser.add_argument('-c', '--clients', default=100, type=int, required=False, dest='clients',
                    help='Number of client you want to create. ')
parser.add_argument('-g', '--genesis', required=True, dest='genesis_path', type=str,
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis')

args = parser.parse_args()
count_failed_clients = 0
rd, wr = multiprocessing.Pipe()
main_loop = asyncio.get_event_loop()
main_loop.add_reader(rd, functools.partial(read_cb, rd))
asyncio.run_coroutine_threadsafe(start_all_procs(args, wr), loop=main_loop)
print("All the processes are started")
try:
    main_loop.run_forever()
except KeyboardInterrupt:
    sys.exit(0)
