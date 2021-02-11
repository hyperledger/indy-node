#!/usr/bin/env python3

from pathlib import Path
import shutil
from sys import argv
script, ledger_name = argv
from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper

config = getConfig()
config_helper = ConfigHelper(config)

def remove(ledger_name):
    exceptions = ["domen", "config", "pool", "audit"]
    if ledger_name not in exceptions:
        for path in Path(config_helper.ledger_data_dir).rglob(ledger_name + "_*"):
            shutil.rmtree(str(path))
            print('The follow directory was deleted: ' + path.name)
    else:
        print('Can`t delete built in ledger: ' + ledger_name)

if __name__ == '__main__':
    remove(ledger_name)
