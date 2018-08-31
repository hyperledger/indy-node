#! /usr/bin/env python3

"""This script uses another load script (perf_processes.py) running it with different parameters which are
provided in config_perf_spike_load.yml file"""


from datetime import timedelta, datetime
import subprocess
import yaml
import time
import os


def create_output_directory(folder_path):
    output_folder = ""
    for folder in folder_path:
        output_folder = os.path.join(output_folder, folder)
    try:
        output_folder = os.path.expanduser(output_folder)
    except OSError:
        raise ValueError("Bad output log folder pathname!")
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    directory = "--directory={}".format(output_folder)
    return directory


def create_subprocess(config, sub_process_type, directory_arg, load_time, load_rate=None):
    args = ["python3", "perf_processes.py"]
    common_args = config["common"].copy()
    common_args.update(config[sub_process_type])
    for dict_key in common_args:
        if dict_key == "directory":
            args.append(directory_arg)
        elif "stepwise" in dict_key:
            continue
        elif load_rate is not None and dict_key == "load_rate":
            args.append("--{}={}".format(dict_key, load_rate))
        else:
            args.append("--{}={}".format(dict_key, common_args[dict_key]))
    args.append("--load_time={}".format(load_time))
    subprocess.Popen(args, close_fds=True)
    return


def start_profile():
    with open("config_perf_spike_load.yml") as file:
        config = yaml.load(file)
    mode = config["profile"]["mode"]
    if mode == "stress":
        stress_profile(config)
    elif mode == "permanent":
        permanent_profile(config)
    elif mode == "spike":
        spike_profile(config)


def run_spikes(config, root_log_folder_name):
    spike_time_in_seconds = config["profile"]["spike_time_in_seconds"]
    folder_count = 0
    key = None
    for key in config["spikes"].keys():
        folder_count += 1
        if config["spikes"][key]["step_time_in_seconds"] != 0:
            sub_process_type = "spike"
            step_time_in_seconds = int(config[key]["stepwise"]["step_time_in_seconds"])
            step_txns_per_second = int(config[key]["stepwise"]["step_txns_per_second"])
            step_load_rate = int(config[key]["stepwise"]["step_initial_load_rate"])
            steps_number = int(spike_time_in_seconds / step_time_in_seconds)

            for i in range(0, steps_number):
                load_time = spike_time_in_seconds - step_time_in_seconds * i
                directory = [config["common"]["directory"], root_log_folder_name,
                             "  {}_{}".format(sub_process_type, folder_count)]
                directory_arg = create_output_directory(directory)
                create_subprocess(config, sub_process_type, directory_arg, load_time, step_load_rate)
                step_load_rate = step_txns_per_second
                time.sleep(step_time_in_seconds)
                folder_count += 1
        else:
            sub_process_type = key
            directory_parts = [config["common"]["directory"], root_log_folder_name,
                               "{}_{}".format(sub_process_type, folder_count)]
            directory_arg = create_output_directory(directory_parts)
            create_subprocess(config, sub_process_type, directory_arg, spike_time_in_seconds)
            print("Spike {}".format(key))
    time.sleep(int(config["profile"]["spike_time_in_seconds"]) +
               int(config["profile"]["rest_time_in_seconds"]))


def spike_profile(config):
    root_log_folder_name = "Spike_log {}".format(time.strftime("%m-%d-%y %H-%M-%S"))

    end_time = datetime.now() + timedelta(seconds=int(config["profile"]["overall_time_in_seconds"]))
    while datetime.now() < end_time:
        run_spikes(config, root_log_folder_name)


def permanent_profile(config):
    root_log_folder_name = "Spike_with_bg_log {}".format(time.strftime("%m-%d-%y %H-%M-%S"))
    directory = [config["common"]["directory"], root_log_folder_name,
                 "{}_{}".format("background", "0")]
    directory_arg = create_output_directory(directory)
    create_subprocess(config, "background", directory_arg, config["profile"]["overall_time_in_seconds"])

    end_time = datetime.now() + timedelta(seconds=int(config["profile"]["overall_time_in_seconds"]))
    while datetime.now() < end_time:
        run_spikes(config, root_log_folder_name)


def stress_profile(config):
    folder_count = 1  # ordering number of the spike which goes to logs folder name
    root_log_folder_name = "Stress_log_{}".format(time.strftime("%m-%d-%y_%H-%M-%S"))
    overall_time_in_seconds = int(config["profile"]["overall_time_in_seconds"])
    sub_process_type = "background"
    if config["background"]["stepwise"]["step_time_in_seconds"] != 0:
        step_time_in_seconds = int(config["background"]["stepwise"]["step_time_in_seconds"])
        step_txns_per_second = int(config["background"]["stepwise"]["step_txns_per_second"])
        step_load_rate = int(config["background"]["stepwise"]["step_initial_load_rate"])
        steps_number = int(overall_time_in_seconds/step_time_in_seconds)

        for i in range(0, steps_number):
            load_time = overall_time_in_seconds - step_time_in_seconds * i
            directory = [config["common"]["directory"], root_log_folder_name,
                         "{}_{}".format(sub_process_type, folder_count)]
            directory_arg = create_output_directory(directory)
            create_subprocess(config, sub_process_type, directory_arg, load_time, step_load_rate)
            step_load_rate = step_txns_per_second
            time.sleep(step_time_in_seconds)
            folder_count += 1
    else:
        directory_parts = [config["common"]["directory"], root_log_folder_name, "Stable_stress"]
        directory_arg = create_output_directory(directory_parts)
        create_subprocess(config, sub_process_type, directory_arg, overall_time_in_seconds)
        print("Stress stable")


if __name__ == '__main__':
    start_profile()
