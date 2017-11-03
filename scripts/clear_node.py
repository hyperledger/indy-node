#!/usr/bin/env python3

import shutil
import os
import argparse
from indy_common.config_util import getConfig


def dirs_to_delete(base_dir, network):
    _base_dir = os.path.expanduser(base_dir)
    if network:
        ret_dir = os.path.join(_base_dir, network)
        if os.path.isdir(ret_dir):
            return [ret_dir]
        else:
            return []
    else:
        return [os.path.join(_base_dir, x) for x in os.listdir(_base_dir) if os.path.isdir(os.path.join(_base_dir, x))]


def clean_files(config, full, network):
    dirs_to_dlt = dirs_to_delete(config.baseDir, network)
    if full:
        dirs_to_dlt = dirs_to_dlt + dirs_to_delete(config.LOG_DIR, network)
        dirs_to_dlt = dirs_to_dlt + dirs_to_delete(config.GENERAL_CONFIG_DIR, network)
    for dir in dirs_to_dlt:
        shutil.rmtree(dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Removes node data and configuration')
    parser.add_argument('--full', required=False, type=bool, default=False, help="remove configs and logs too")
    parser.add_argument('--network', required=False, type=str, help="Network to clean")
    args = parser.parse_args()
    config = getConfig()
    clean_files(config, args.full, args.network)
