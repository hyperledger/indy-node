import argparse
import time
from datetime import timedelta, datetime
import subprocess


parser = argparse.ArgumentParser(description='The script uses another load script with different parameters')

parser.add_argument('-c', '--clients', default=0, type=int, required=False, dest='clients',
                    help='Number of client you want to create. '
                         '0 or less means equal to number of available CPUs. '
                         'Default value is 0')

parser.add_argument('--read_mode', default='permanent', type=str, required=False, dest='read_mode',
                    help='Load profile for reading transactions. '
                         'Permanent - stable background load, '
                         'spike - raises sharply along with writing transaction spikes. '
                         'Default value is permanent')

parser.add_argument('--read_per_second', default=100, type=int, required=False, dest='rps',
                    help='Load rate for reading transactions, txn/sec')

parser.add_argument('--write_per_second', default=10, type=int, required=False, dest='wps',
                    help='Load rate for writing transactions, txn/sec')

parser.add_argument('-g', '--genesis', required=False, type=str, dest='genesis_path',
                    help='Path to genesis txns file. '
                         'Default value is ~/.indy-cli/networks/sandbox/pool_transactions_genesis',
                    default="~/.indy-cli/networks/sandbox/pool_transactions_genesis")

parser.add_argument('--overall_time', default=600, type=int, required=False, dest='overall_time_in_minutes',
                    help='Test execution time in minutes. '
                    'Default value is 600 (10 hours)')

parser.add_argument('--spike_time', default=10, type=int, required=False, dest='spike_time_in_minutes',
                    help='Time of every spike, minutes. '
                    'Default time is 10 minutes')

parser.add_argument('--rest_time', default=10, type=int, required=False, dest='rest_time_in_minutes',
                    help='Time between spikes, minutes. '
                    'Default time is 10 minutes')

parser.add_argument('--read_kind', default='get_nym', type=str, required=False, dest='read_kind',
                    help='Kind of reading transactions. '
                    'Default is get_nym')

parser.add_argument('--write_kind', default='nym', type=str, required=False, dest='write_kind',
                    help='Kind of writing transactions. '
                    'Default is nym')

parser.add_argument('-d', '--directory', default=".", required=False, dest='out_dir',
                    help='Directory to save output files. Default value is "."')


def create_subprocess_args(additional_args):
    subprocess_template = ["python3", "perf_processes.py", "-n=1", "-y=all", "-b=100"]
    subprocess_template.extend(additional_args)
    return subprocess_template


def start_profile(args):
    genesis_arg = "-g=%s" % args.genesis_path
    output_arg = "-d=%s" %args.out_dir
    overall_time_arg = "--load_time=%s" % str(int(args.overall_time_in_minutes) * 60)
    read_kind_arg = "-k=%s" % args.read_kind
    write_arg_kind = "-k=%s" % args.write_kind
    rps_arg = "-l=%s" % args.rps
    wps_arg = "-l=%s" % args.wps
    clients_arg = "-c=%s" %args.clients
    spike_time_in_seconds = int(args.spike_time_in_minutes) * 60
    spike_time_arg = "--load_time=%s" % str(spike_time_in_seconds)
    rest_time_in_seconds = int(args.rest_time_in_minutes) * 60

    if args.read_mode == 'permanent':
        # start profile with reading transactions for the whole time
        subprocess_args = create_subprocess_args([genesis_arg, output_arg, rps_arg, read_kind_arg, overall_time_arg,
                                                  clients_arg])
        subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
    end_time = datetime.now() + timedelta(minutes=int(args.overall_time_in_minutes))
    while datetime.now() < end_time:
        if args.read_mode != 'permanent':
            # start profile with reading transactions for x minutes
            subprocess_args = create_subprocess_args([genesis_arg, output_arg, rps_arg, read_kind_arg, spike_time_arg,
                                                      clients_arg])
            subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
        # start profile with writing transactions for x minutes
        subprocess_args = create_subprocess_args([genesis_arg, output_arg, wps_arg, write_arg_kind, spike_time_arg,
                                                  clients_arg])
        subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(rest_time_in_seconds + spike_time_in_seconds)


if __name__ == '__main__':
    args = parser.parse_args()
    start_profile(args)
    start_profile(args)