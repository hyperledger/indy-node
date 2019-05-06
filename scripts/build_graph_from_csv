#! /usr/bin/env python3

"""
This script parses csv log file and builds a graph

Plot list: plot1/plot2/.../plotN

Plot: Title[,options]:graph1,graph2,...,graphN

Options:
    log - log scale Y axis

Graph:
    avg_metric           - average metric value in window
    min_metric           - minimum metric value in window
    max_metric           - maximum metric value in window
    lo_metric            - lower metric value within stddev range from average
    hi_metric            - higher metric value within stddev range from average
    tol_metric           - lo, avg, hi combined
    stats_metric         - min, lo, avg, hi, max combined
    metric_per_sec       - sum of metric values averaged over frame time
    metric_count_per_sec - number of metric events averaged over frame time

An option --output allows user to define a filepath for an output image (e.g. --output /home/me/Documents/out.png).
If this option is provided, the script will not display the figure on a screen.
"""

from typing import List

from matplotlib import pyplot as plt
from collections import namedtuple
from datetime import datetime
import pandas as pd
import argparse
import os


def add_subplot(ax, name, items, data, log_scale=False):
    ax.set_title(name, verticalalignment='center')
    ax.grid(True)
    ax.set_yscale("log" if log_scale else "linear")

    timestamps = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in data.timestamp]

    for item in items:
        ax.plot(timestamps, data[item], label=item, ls='-', lw=2)
    ax.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)

PlotInfo = namedtuple('GraphInfo', 'title log_scale items')


def parse_plot_info(text: str) -> PlotInfo:
    title, items = text.split(':')
    if ',' in title:
        params = title.split(',')
        title = params[0]
        params = params[1:]
    else:
        params = []
    items = items.split(',')
    all_items = []
    for item in items:
        if item.startswith('tol_'):
            base = item[4:]
            all_items.append('lo_{}'.format(base))
            all_items.append('avg_{}'.format(base))
            all_items.append('hi_{}'.format(base))
        elif item.startswith('stats_'):
            base = item[6:]
            all_items.append('min_{}'.format(base))
            all_items.append('lo_{}'.format(base))
            all_items.append('avg_{}'.format(base))
            all_items.append('hi_{}'.format(base))
            all_items.append('max_{}'.format(base))
        else:
            all_items.append(item)
    return PlotInfo(title=title, log_scale=('log' in params), items=all_items)


def parse_plot_list(text: str) -> List[PlotInfo]:
    return [parse_plot_info(s) for s in text.split('/')]


def build_graph():
    plt.rcParams.update({'font.size': 10})
    plt.rcParams["figure.figsize"] = [23,12]

    parser = argparse.ArgumentParser(description='Gets file path and graph name to build a graph')
    parser.add_argument('--output', required=False, help='output picture file path', dest="output")
    parser.add_argument('filepath', type=str, help='the csv file absolute path')
    parser.add_argument('--plots', required=False, help='plot list')
    args = parser.parse_args()
    file_path = args.filepath
    file = pd.read_csv(file_path)

    if args.plots:
        plot_list = parse_plot_list(args.plots)
    else:
        plot_list = [
            PlotInfo(title="Throughput", log_scale=False,
                     items=["client_stack_messages_processed_per_sec",
                            "ordered_batch_size_per_sec"]),
            PlotInfo(title="Backup throughput", log_scale=False,
                     items=["backup_ordered_batch_size_per_sec"]),
            PlotInfo(title="Latency", log_scale=False,
                     items=["avg_monitor_avg_latency",
                            "avg_backup_monitor_avg_latency"]),
            PlotInfo(title="Messages per iteration", log_scale=False,
                     items=["avg_node_stack_messages_processed",
                            "avg_client_stack_messages_processed"]),
            PlotInfo(title="Traffic", log_scale=True,
                     items=["incoming_node_message_size_per_sec",
                            "outgoing_node_message_size_per_sec",
                            "incoming_client_message_size_per_sec",
                            "outgoing_client_message_size_per_sec"]),
            PlotInfo(title="Request queues", log_scale=False,
                     items=["avg_request_queue_size",
                            "avg_finalised_request_queue_size",
                            "avg_monitor_request_queue_size",
                            "avg_monitor_unordered_request_queue_size"]),
            PlotInfo(title="View change", log_scale=False,
                     items=["max_view_change_in_progress"]),
            PlotInfo(title="View no", log_scale=False,
                     items=["max_current_view"]),
            PlotInfo(title="Memory", log_scale=False,
                     items=["avg_node_rss_size"]),
            PlotInfo(title="Looper", log_scale=True,
                     items=["avg_looper_run_time_spent",
                            "avg_node_prod_time",
                            "max_node_prod_time"])]

    fig, axs = plt.subplots(len(plot_list), 1, sharex=True)
    fig.autofmt_xdate()
    if len(plot_list) == 1:
        axs = [axs]

    for plot, ax in zip(plot_list, axs):
        add_subplot(ax, plot.title, plot.items, file, log_scale=plot.log_scale)

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.subplots_adjust(left=0.05, right=0.85, bottom=0.07, top=0.93)
    plt.suptitle(file_path)

    if not args.output:
        plt.show()
    else:
        output = os.path.expanduser(args.output)
        plt.savefig(output, bbox_inches='tight')

if __name__ == '__main__':
    build_graph()
