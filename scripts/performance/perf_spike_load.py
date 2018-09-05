#! /usr/bin/env python3


import subprocess
import yaml
import time
import os
import collections
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='This script uses another load script (perf_processes.py) running it '
                                             'with different parameters which are provided in '
                                             'config_perf_spike_load.yml file')

parser.add_argument('-g', '--graph', default=False, type=bool, required=False, dest='graph',
                    help='Build a graph to check if the configured profile is correct')

args = parser.parse_args()


def create_output_directory(folder_path):
    output_folder = os.path.join(folder_path[0], *folder_path[1:])
    try:
        output_folder = os.path.expanduser(output_folder)
    except OSError:
        raise ValueError("Bad output log folder pathname!")
    if not os.path.isdir(output_folder) and not args.graph:
        os.makedirs(output_folder)
    directory = "--directory={}".format(output_folder)
    return directory


def get_args(config, process_type, directory_arg):
    args_for_script = ["python3", "perf_processes.py"]
    common_args = config["common"].copy()
    common_args.update(config["processes"][process_type])
    for dict_key in common_args:
        if dict_key == "directory":
            args_for_script.append(directory_arg)
        elif "step" in dict_key:
            continue
        else:
            args_for_script.append("--{}={}".format(dict_key, common_args[dict_key]))
    return args_for_script


def order_processes(delays, args_for_script):
    assert len(delays) == len(args_for_script), 'Can not order the processes as a list of delays length is not equal ' \
                                                'to a list of arguments length.'
    unique_delays = set(delays)
    processes_dictionary = {}
    for delay in unique_delays:
        delays_indices = [i for i, e in enumerate(delays) if e == delay]
        args_list = []
        for index in delays_indices:
            args_list.append(args_for_script[index])
        processes_dictionary.update({delay: args_list})
    processes_dictionary_sorted = collections.OrderedDict(sorted(processes_dictionary.items()))
    return processes_dictionary_sorted


def collect_delays(function_parameters, time_interval, spike_delay=0):
    args_for_script = function_parameters[0]
    step_time = function_parameters[1]
    step_initial_load = function_parameters[2]
    step_final_load = function_parameters[3]
    args_copy = args_for_script.copy()
    args_to_send = []
    delay = []
    if step_time != 0 and step_final_load != step_initial_load:
        step_number = int(time_interval / step_time)
        step_value = int((step_final_load - step_initial_load) / step_number)
        if step_value == 0:
            raise ValueError("There should be at least one transaction per step.")
        for i in range(0, step_number):
            load_time = time_interval - step_time * i
            args_copy = args_for_script.copy()
            args_copy.append("--load_time={}".format(load_time))
            if i != 0:
                args_copy.append("--load_rate={}".format(step_value))
            else:
                args_copy.append("--load_rate={}".format(step_initial_load))
            delay.append(spike_delay + time_interval - load_time)
            args_to_send.append(args_copy)
            step_number += 1
    else:
        delay.append(spike_delay)
        args_copy.append("--load_time={}".format(time_interval))
        args_copy.append("--load_rate={}".format(step_initial_load))
        args_to_send.append(args_copy)
    return [delay, args_to_send]


def collect_processes(config):
    root_log_folder_name = "Spike_log_{}".format(time.strftime("%m-%d-%y_%H-%M-%S"))
    processes = list(config["processes"].keys())
    functions = {}
    for process_name in processes:
        step_time_in_seconds = config["processes"][process_name]["step_time_in_seconds"]
        if step_time_in_seconds == 0:
            continue
        initial_rate = config["processes"][process_name]["step_initial_load_rate"]
        final_rate = config["processes"][process_name]["step_final_load_rate"]
        if initial_rate > final_rate:
            raise ValueError("In {} block initial rate is bigger than final!".format(process_name))
        directory = [config["common"]["directory"], root_log_folder_name, process_name]
        directory_arg = create_output_directory(directory)
        args_for_script = get_args(config, process_name, directory_arg)
        step_parameters = [args_for_script, step_time_in_seconds, initial_rate, final_rate]
        functions.update({process_name: step_parameters})
    return functions


def start_profile():
    with open("config_perf_spike_load.yml") as file:
        config = yaml.load(file)
    spike_time = config["profile"]["spike_time_in_seconds"]
    rest_time = config["profile"]["rest_time_in_seconds"]
    overall_time_in_seconds = int(config["profile"]["overall_time_in_seconds"])
    delays_list = []
    args_list = []
    background_plot = []
    processes_dict = collect_processes(config)
    if "background" in list(processes_dict.keys()):
        delays_args_list = collect_delays(processes_dict["background"], overall_time_in_seconds)
        delays_list.extend(delays_args_list[0])
        args_list.extend(delays_args_list[1])
        background_plot = prepare_plot_values(delays_args_list)

    spike_plots_list = []
    time_count = 0
    spikes_list = filter(lambda i: "background" not in i, list(processes_dict.keys()))
    spike_number = 0
    for spike in spikes_list:
        while time_count < overall_time_in_seconds:
            spike_delay = (spike_time + rest_time) * spike_number
            delays_args_list = (collect_delays(processes_dict[spike], spike_time, spike_delay))
            delays_list.extend(delays_args_list[0])
            args_list.extend(delays_args_list[1])
            spike_plots_list.append(prepare_plot_values(delays_args_list))
            spike_number += 1
            time_count += spike_time + rest_time

        spike_number = 0
        time_count = 0

    if args.graph:
        build_plot_on_config(background_plot, spike_plots_list)
    else:
        prepared = order_processes(delays_list, args_list)
        time_count = 0
        for item in prepared.keys():
            time.sleep(item - time_count)
            for process_args in prepared[item]:
                subprocess.Popen(process_args, close_fds=True)
            time_count = item


def prepare_plot_values(delays_args_list):
    delays = delays_args_list[0]
    args_for_script = delays_args_list[1]
    plot_dict = {}
    for i in range(0, len(delays)):
        plot_dict.update({delays[i]: int(args_for_script[i][-1].split("=")[-1])})
    plot_dict_sorted = collections.OrderedDict(sorted(plot_dict.items()))
    return plot_dict_sorted


def add_plot(ax, args_dict, color):
    step_count = 1
    time_ax = []
    load_rate = []
    for delay in args_dict.keys():
        step_load_rate = args_dict[delay]
        time_ax.append(delay)
        if step_count != 1:
            load_rate.append(load_rate[0] + step_load_rate * (step_count - 1))
        else:
            load_rate.append(step_load_rate)
        step_count += 1
    time_ax.append((time_ax[-1] - time_ax[-2]) + time_ax[-1])
    load_rate.append((load_rate[-1] - load_rate[-2]) + load_rate[-1])
    ax.fill_between(time_ax, load_rate, facecolor=color, alpha=0.4)


def build_plot_on_config(background, spikes):
    figure, ax = plt.subplots(1, 1)
    if len(background) != 0:
        add_plot(ax, background, 'b')
    if len(spikes) != 0:
        for spike in spikes:
            add_plot(ax, spike, 'g')
    start, stop = ax.get_ylim()
    ticks = np.arange(start, stop + (stop // 10), stop // 10)
    ax.set_yticks(ticks)
    ax.grid()
    plt.show()


if __name__ == '__main__':
    start_profile()
