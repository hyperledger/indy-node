import argparse
import json
import time
import asyncio

from multiprocessing import Process, Pipe

import os

import functools

import sys
from indy import pool

count_of_connected = 0
count_of_not_connected = 0
client_connections_node_limit = 100
pool_size = 4
max_failure_tolerance = 1


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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(
            run_test(genesis_path, loop, pipe_conn)
        ))
    except Exception as e:
        pipe_conn.send(e)


def get_max_connected_clients_without_stack_restart(limit, N, F):
    return int(limit * (N / (N - F)))


def read_cb(pipe_conn):
    global count_of_connected
    global count_of_not_connected
    global max_connected_clients_without_stack_restart
    global arg_clients_num
    res = pipe_conn.recv()
    if isinstance(res, tuple):
        code, cl_number = res
        if code == 0:
            print("Client with number {} is connected".format(cl_number))
            count_of_connected += 1
        elif code == 1:
            print("Client with number {} is not connected".format(cl_number))
            count_of_not_connected += 1
        print("===============================================")
        print("Count of connected clients:     {}".format(count_of_connected))
        print("Count of not connected clients: {}".format(count_of_not_connected))
        print("===============================================")
        if count_of_connected + count_of_not_connected == arg_clients_num:
            result_str = "\n===== TEST {}: connected clients {}, not connected clients {}, max(limit, N, F) {} =====".\
                format("PASSED" if count_of_connected > max_connected_clients_without_stack_restart else "FAILED",
                       count_of_connected,
                       count_of_not_connected,
                       max_connected_clients_without_stack_restart)
            print(result_str)

    else:
        print(res)


async def start_all_procs(args, wr):
    global client_connections_node_limit
    processes = []
    for client_number in range(args.clients):
        if client_number == client_connections_node_limit:
            # Give a chance all clients that fit the limit to connect
            time.sleep(10)
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
arg_clients_num = args.clients

count_failed_clients = 0
max_connected_clients_without_stack_restart = \
    get_max_connected_clients_without_stack_restart(
        client_connections_node_limit, pool_size, max_failure_tolerance)

rd, wr = Pipe()
main_loop = asyncio.get_event_loop()
main_loop.add_reader(rd, functools.partial(read_cb, rd))
print("Connecting clients...")
asyncio.run_coroutine_threadsafe(start_all_procs(args, wr), loop=main_loop)
try:
    main_loop.run_forever()
except KeyboardInterrupt:
    sys.exit(0)
