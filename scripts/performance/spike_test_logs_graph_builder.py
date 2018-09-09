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
        i += 1
    return len(values)


def add_graph(values, color):
    load_coefficient = 0
    time_ax = []
    load_ax = []
    spike_length = get_spike_length(values)
    for i in range(0, len(values)):
        if i % spike_length == 0:
            load_coefficient = 0
        time_ax.extend([values[i][0], values[i][0]])
        load_ax.append(values[i][2] * load_coefficient)
        load_coefficient += 1
        load_ax.append(values[i][2] * load_coefficient)
        if (i + 1) % spike_length == 0 and i != 0:
            time_ax.extend([values[i][1], values[i][1]])
            load_ax.extend([values[i][2] * load_coefficient, 0])
    plt.fill_between(time_ax, load_ax, facecolor=color, alpha=0.4)


def build_graph():
    input_values = pandas.read_csv(args.log_file, header=None)
    background_values = []
    spike_values = []
    for row in input_values.values:
        process_name = row[1]
        length = row[3]
        time_start = datetime.datetime.strptime(row[0], '%m-%d-%Y %H:%M:%S')
        time_end = time_start + datetime.timedelta(seconds=length)
        load_rate = row[2]
        if process_name == "background":
            background_values.append([time_start, time_end, load_rate, length])
        elif process_name == "spike":
            spike_values.append([time_start, time_end, load_rate, length])
    add_graph(background_values, 'blue')
    add_graph(spike_values, 'green')
    plt.show()


if __name__ == '__main__':
    args = parser.parse_args()
    build_graph()
