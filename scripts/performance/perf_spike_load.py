import time
from datetime import timedelta, datetime
import subprocess
import yaml


def create_subprocess_args(config, sub_process_type):
    args = ["python3", "perf_processes.py"]
    common_args = config["common"]
    for dict_key in common_args:
        args.append("--" + dict_key + "=" + str(common_args[dict_key]))
    if sub_process_type == "read_background":
        args.append("--load_time=" + str(config["perf_spike"]["overall_time_in_seconds"]))
        args.append("--load_rate=" + str(config["read_txns"]["load_rate"]))
        args.append("--kind=" + str(config["read_txns"]["kind"]))
    elif sub_process_type == "read_spike":
        args.append("--load_time=" + str(config["perf_spike"]["spike_time_in_seconds"]))
        args.append("--load_rate=" + str(config["read_txns"]["load_rate"]))
        args.append("--kind=" + str(config["read_txns"]["kind"]))
    elif sub_process_type == "write_spike":
        args.append("--load_time=" + str(config["perf_spike"]["spike_time_in_seconds"]))
        args.append("--load_rate=" + str(config["write_txns"]["load_rate"]))
        args.append("--kind=" + str(config["write_txns"]["kind"]))
    return args


def start_profile():
    with open("config_perf_spike_load.yml") as file:
        config = yaml.load(file)
    if config["perf_spike"]["read_mode"] == 'permanent':
        subprocess_args = create_subprocess_args(config, "read_background")
        print(subprocess_args)
        subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
    end_time = datetime.now() + timedelta(seconds=int(config["perf_spike"]["overall_time_in_seconds"]))
    while datetime.now() < end_time:
        if config["perf_spike"]["read_mode"] == 'spike':
            # start profile with reading transactions for x minutes
            subprocess_args = create_subprocess_args(config, "read_spike")
            subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
            time.sleep(2) # log folders cannot be created for 2 scripts launched at the same time
        # start profile with writing transactions for x minutes
        subprocess_args = create_subprocess_args(config, "write_spike")
        subprocess.Popen(subprocess_args, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(int(config["perf_spike"]["spike_time_in_seconds"]) + int(config["perf_spike"]["rest_time_in_seconds"]))


if __name__ == '__main__':
    start_profile()
