#!/usr/bin/env python3

from pathlib import Path
import shutil
from sys import argv
script, file_path = argv
from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper

config = getConfig()
config_helper = ConfigHelper(config)

def main(file_path):
    exceptions = ["domen", "config", "pool", "audit"]
    if file_path not in exceptions:
        for path in Path(config_helper.ledger_data_dir).rglob(file_path + "_*"):
            shutil.rmtree(str(path))
            print('follow directory was deleted: ' + path.name)
    else:
        print('Can`t delete ledger: ' + file_path)

if __name__ == '__main__':
    main(file_path)
