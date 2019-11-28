#!/usr/bin/env python3

import shutil
import argparse
from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper


def clean(config, full, network_name):
    if network_name:
        config.NETWORK_NAME = network_name
    config_helper = ConfigHelper(config)

    shutil.rmtree(config_helper.log_dir)
    shutil.rmtree(config_helper.keys_dir)
    shutil.rmtree(config_helper.genesis_dir)

    if full:
        shutil.rmtree(config_helper.ledger_base_dir)
        shutil.rmtree(config_helper.log_base_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Removes node data and configuration')
    parser.add_argument('--full', required=False, type=bool, default=False, help="remove configs and logs too")
    parser.add_argument('--network', required=False, type=str, help="Network to clean")
    args = parser.parse_args()
    config = getConfig()
    clean(config, args.full, args.network)
