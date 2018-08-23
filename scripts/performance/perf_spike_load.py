#! /usr/bin/env python3

"""This script uses another load script (perf_processes.py) running it with different parameters which are
provided in config_perf_spike_load.yml file"""


from datetime import timedelta, datetime
import subprocess
import yaml
import time
import os


def create_subprocess_args(config, sub_process_type, folder_count, log_folder_name):
    args = ["python3", "perf_processes.py"]
    common_args = config["common"].copy()
    if "read" in sub_process_type:
        common_args.update(config["read_txns"])
    elif "write" in sub_process_type:
        common_args.update(config["write_txns"])
    for dict_key in common_args:
        if dict_key == "directory":
            output_folder = os.path.join(str(common_args[dict_key]), log_folder_name,
                                         "{}_{}".format(sub_process_type, folder_count))
            try:
                output_folder = os.path.expanduser(output_folder)
            except OSError:
                raise ValueError("Bad output log folder pathname!")
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            args.append("--{}={}".format(dict_key, output_folder))
        else:
            args.append("--{}={}".format(dict_key, common_args[dict_key]))
    if "background" in sub_process_type:
        args.append("--load_time={}".format(config["perf_spike"]["overall_time_in_seconds"]))
    elif "spike" in sub_process_type:
        args.append("--load_time={}".format(config["perf_spike"]["spike_time_in_seconds"]))
    return args


def start_profile():
    folder_count = 0  # ordering number of the spike which goes to logs folder name
    root_log_folder_name = "Spike_log {}".format(time.strftime("%m-%d-%y %H-%M-%S"))
    with open("config_perf_spike_load.yml") as file:
        config = yaml.load(file)
    if config["perf_spike"]["read_mode"] == 'permanent':
        subprocess_args = create_subprocess_args(config, "read_background", folder_count, root_log_folder_name)
        subprocess.Popen(subprocess_args, close_fds=True)
    end_time = datetime.now() + timedelta(seconds=int(config["perf_spike"]["overall_time_in_seconds"]))
    while datetime.now() < end_time:
        folder_count += 1
        if config["perf_spike"]["read_mode"] == 'spike':
            # start profile with reading transactions for x minutes
            subprocess_args = create_subprocess_args(config, "read_spike", folder_count, root_log_folder_name)
            subprocess.Popen(subprocess_args, close_fds=True)
            folder_count += 1
        # start profile with writing transactions for x minutes
        subprocess_args = create_subprocess_args(config, "write_spike", folder_count, root_log_folder_name)
        subprocess.Popen(subprocess_args, close_fds=True)
        time.sleep(int(config["perf_spike"]["spike_time_in_seconds"]) +
                   int(config["perf_spike"]["rest_time_in_seconds"]))


if __name__ == '__main__':
    start_profile()
