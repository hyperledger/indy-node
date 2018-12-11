#! /usr/bin/env python3

import subprocess
import yaml
import time
import os
import threading
import logging
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--file', required=False, default="spike_log.csv",
                    help="Output CSV file name with logs", dest="log_file")

parser.add_argument('--spike_config', required=False, default="config_perf_spike_load.yml",
                    help="Path to config for spike load test in YML format", dest="spike_config")


def create_output_directory(folder_path):
    output_folder = os.path.join(folder_path[0], *folder_path[1:])
    try:
        output_folder = os.path.expanduser(output_folder)
    except OSError:
        raise ValueError("Bad output log folder pathname!")
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    return output_folder


def get_args(test_config, process_name):
    args_for_script = ["perf_processes.py"]
    common_args = test_config["common"].copy()
    common_args.update(test_config["processes"][process_name])
    for dict_key, dict_value in common_args.items():
        if dict_key == "out_dir":
            directory = create_output_directory([test_config["common"]["out_dir"], "Spike_log", process_name])
            args_for_script.append("--out_dir={}".format(directory))
        elif "step" in dict_key or dict_key == "mode":
            continue
        else:
            args_for_script.append("--{}={}".format(dict_key, dict_value))
    return args_for_script


def start_load_script(args_for_script, rate, load_time):
    args_for_script.append("--load_rate={}".format(rate))
    args_for_script.append("--load_time={}".format(load_time))
    subprocess.Popen(args_for_script, close_fds=True)


def background(test_config, background_fn):
    total_test_time = test_config["profile"]["total_time_in_seconds"]
    background_mode = test_config["processes"]["background"]["mode"]
    background_fn("background", test_config, total_test_time)
    if total_test_time == 0 and background_mode == "stepwise":
        while True:
            background_fn("background", test_config, total_test_time)


def spikes(test_config, spike_fn):
    total_test_time = test_config["profile"]["total_time_in_seconds"]
    spike_time = test_config["profile"]["spike_time_in_seconds"]
    rest_time = test_config["profile"]["rest_time_in_seconds"]
    interval = 0
    spike_mode = test_config["processes"]["spike"]["mode"]
    if spike_mode == "stepwise":
        interval = test_config["profile"]["rest_time_in_seconds"]
    elif spike_mode == "stable":
        interval = test_config["profile"]["rest_time_in_seconds"] + spike_time
    if total_test_time == 0:
        while True:
            spike_fn("spike", test_config, spike_time, interval)
    else:
        while total_test_time > 0:
            spike_fn("spike", test_config, spike_time, interval)
            total_test_time -= (spike_time + rest_time)


def run_stepwise_process(process_name, test_config, process_time, interval=0):
    initial_rate = test_config["processes"][process_name]["step_initial_load_rate"]
    step_value = test_config["processes"][process_name]["step_value"]
    step_time = test_config["processes"][process_name]["step_time_in_seconds"]
    script_args = get_args(test_config, process_name)
    if process_time != 0:
        process_time_count = process_time
        step_count = 0
        if initial_rate != 0:
            start_load_script(script_args, initial_rate, process_time)
            logging.info(",{},{},{}".format(process_name, initial_rate, process_time))
            process_time_count -= step_time
            step_count = 1
            time.sleep(step_time)
        else:
            process_time_count = process_time
        while process_time_count > 0:
            start_load_script(script_args, step_value, process_time_count)
            sleep = min(step_time, process_time - step_time * step_count)
            logging.info(",{},{},{}".format(process_name, step_value, process_time_count))
            process_time_count -= step_time
            time.sleep(sleep)
            step_count += 1
        time.sleep(interval)
    else:
        start_load_script(script_args, step_value, process_time)
        logging.info(",{},{},{}".format(process_name, step_value, process_time))
        time.sleep(step_time)


def run_stable_process(process_name, config, process_time, interval=0):
    initial_rate = config["processes"][process_name]["step_initial_load_rate"]
    script_args = get_args(config, process_name)
    start_load_script(script_args, initial_rate, process_time)
    logging.info(",{},{},{}".format(process_name, initial_rate, process_time))
    time.sleep(interval)


def start_profile():
    with open(args.spike_config) as file:
        test_config = yaml.load(file)
    logging_folder = create_output_directory([test_config["common"]["out_dir"], "Spike_log"])
    logging_file_path = os.path.join(logging_folder, args.log_file)
    logging.basicConfig(filename=logging_file_path, filemode='w', level=logging.INFO,
                        format='%(asctime)s%(message)s', datefmt='%m-%d-%y %H:%M:%S')
    logging.Formatter.converter = time.gmtime
    background_mode = test_config["processes"]["background"]["mode"]
    spike_mode = test_config["processes"]["spike"]["mode"]
    thread1 = None
    thread2 = None
    if background_mode == "stepwise":
        thread1 = threading.Thread(target=background, args=(test_config, run_stepwise_process))
        thread1.start()
    elif background_mode == "stable":
        thread1 = threading.Thread(target=background, args=(test_config, run_stable_process))
        thread1.start()
    if spike_mode == "stepwise":
        thread2 = threading.Thread(target=spikes, args=(test_config, run_stepwise_process))
        thread2.start()
    elif spike_mode == "stable":
        thread2 = threading.Thread(target=spikes, args=(test_config, run_stable_process))
        thread2.start()
    if thread1:
        thread1.join()
    if thread2:
        thread2.join()


if __name__ == '__main__':
    args = parser.parse_args()
    start_profile()
