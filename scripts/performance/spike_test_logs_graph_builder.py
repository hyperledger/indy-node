#! /usr/bin/env python3

import matplotlib.pyplot as plt
import datetime
import pandas
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--file', required=False, default="./spike_log.csv",
                    help="Input CSV file name with logs", dest="log_file")


def get_spike_length(values):
    first_spike_start = values[0][3]
    for i in range(1, len(values)):
        if values[i][3] == first_spike_start:
            return i
    return len(values)


def get_final_time(input_values):
    times = []
    for row in input_values.values:
        times.append(datetime.datetime.strptime(row[0], '%m-%d-%y %H:%M:%S'))
    return max(times)


def add_bg_graph(values, color):
    load_coefficient = 0
    time_ax = []
    load_ax = []
    initial_rate = values[0][2]
    for i in range(0, len(values)):
        if i == 0:
            load_coefficient = 0
            time_ax.extend([values[i][0], values[i][0]])
            load_ax.extend([0, initial_rate])
        else:
            time_ax.extend([values[i][0], values[i][0]])
            load_ax.append(initial_rate + values[i][2] * load_coefficient)
            load_coefficient += 1
            load_ax.append(initial_rate + values[i][2] * load_coefficient)
        if i == len(values) - 1:
            time_ax.extend([values[i][1], values[i][1]])
            load_ax.extend([initial_rate + values[i][2] * load_coefficient, 0])
    plt.fill_between(time_ax, load_ax, facecolor=color, alpha=0.4)


def add_graph(values, color):
    load_coefficient = 0
    time_ax = []
    load_ax = []
    spike_length = get_spike_length(values)
    initial_rate = values[0][2]
    for i in range(0, len(values)):
        if i % spike_length == 0:
            load_coefficient = 0
            time_ax.extend([values[i][0], values[i][0]])
            load_ax.extend([0, initial_rate])
        else:
            time_ax.extend([values[i][0], values[i][0]])
            load_ax.append(initial_rate + values[i][2] * load_coefficient)
            load_coefficient += 1
            load_ax.append(initial_rate + values[i][2] * load_coefficient)
        if (i + 1) % spike_length == 0:
            time_ax.extend([values[i][1], values[i][1]])
            load_ax.extend([initial_rate + values[i][2] * load_coefficient, 0])
    plt.fill_between(time_ax, load_ax, facecolor=color, alpha=0.4)


def build_graph():
    input_values = pandas.read_csv(args.log_file, header=None)
    background_values = []
    spike_values = []
    final_time = get_final_time(input_values)
    for row in input_values.values:
        process_name = row[1]
        length = row[3]
        time_start = datetime.datetime.strptime(row[0], '%m-%d-%y %H:%M:%S')
        if length == 0:
            time_end = final_time
        else:
            time_end = time_start + datetime.timedelta(seconds=length)
        load_rate = row[2]
        if process_name == "background":
            background_values.append([time_start, time_end, load_rate, length])
        elif process_name == "spike":
            spike_values.append([time_start, time_end, load_rate, length])
    if len(spike_values) != 0:
        add_graph(spike_values, 'green')
    if len(background_values) != 0:
        add_bg_graph(background_values, 'blue')
    plt.xticks(rotation=15)
    plt.show()


if __name__ == '__main__':
    args = parser.parse_args()
    build_graph()
