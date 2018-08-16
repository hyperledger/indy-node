import argparse
import time
from datetime import date, timedelta, datetime
import subprocess
import random


parser = argparse.ArgumentParser(description='The script another load script with different paramters')

parser.add_argument('--read_mode', default='permanent', type=str, required=False, dest='read_mode',
                    help='Load profile for reading transactions'
                         'permanent - stable background load'
                         'spike - raises sharply along with writing transaction spikes'
                         'Default value is permanent')

parser.add_argument('--read_per_second', default=100, type=int, required=False, dest='rps',
                    help='Load rate for reading transactions, txn/sec')

parser.add_argument('--write_per_second', default=10, type=int, required=False, dest='wps',
                    help='Load rate for writing transactions, txn/sec')

parser.add_argument('-g', '--genesis', required=False, dest='genesis_path',
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis")

parser.add_argument('--overall_time', default=600, type=int, required=False, dest='overall_time_in_minutes',
                    help='Test execution time in minutes. '
                    'Default value is 600 (10 hours)')

parser.add_argument('--spike_time', default=10, type=int, required=False, dest='spike_time_in_minutes',
                    help='Time of every spike, minutes'
                    'Default time is 10 minutes')

parser.add_argument('--rest_time', default=10, type=int, required=False, dest='rest_time_in_minutes',
                    help='Time between spikes, minutes'
                    'Default time is 10 minutes')

parser.add_argument('--read_kind', default='random', type=str, required=False, dest='read_kind',
                    help='Kind of reading transactions'
                    'Default is random')

parser.add_argument('--write_kind', default='random', type=str, required=False, dest='write_kind',
                    help='Kind of writing transactions'
                    'Default is random')


start_time = datetime.now()
read_txn = ["get_nym", "get_attrib", "get_schema", "get_cred_def", "get_revoc_reg", "get_revoc_reg_delta"]
write_txn = ["nym", "schema", "attrib", "cred_def"]  # revoc_reg_entry


def start_profile(args):
    if args.read_kind == 'random':
        read_kind = random.choice(read_txn)
    else:
        read_kind = args.read_kind
    if args.write_kind == 'random':
        write_kind = random.choice(write_txn)
    else:
        write_kind = args.write_kind
    if args.read_mode == 'permanent':
        # start profile with reading transactions for the whole time
        subprocess.run(["python3", "perf_processes.py"
                        , "-g %s" % args.genesis_path
                        , "-l %s" % args.rps
                        , "-k %s" % read_kind
                        , "--load_time %s" % args.overall_tim_in_minutes * 60])
    end_time = start_time + timedelta(minutes=args.overall_time_in_minutes * 60)
    while datetime.now() < end_time:
        if args.read_mode != 'permanent':
            # start profile with reading transactions for x minutes
            subprocess.run(["python3", "perf_processes.py"
                            , "-g %s" % args.genesis_path
                            , "-l %s" % args.rps
                            , "-k %s" % read_kind
                            ,  "--load_time %s" % args.spike_time_in_minutes * 60])
        # start profile with writing transactions for x minutes
        subprocess.run(["python3", "perf_processes.py"
                        , "-g %s" % args.genesis_path
                        , "-l %s" % args.wps
                        , "-k %s" % write_kind
                        , "--load_time %s" % args.spike_time_in_minutes * 60])
        time.sleep(args.rest_time)


if __name__ == '__main__':
    args = parser.parse_args()
    start_profile(args)