#!/usr/bin/env python3

from pathlib import Path
import shutil
from sys import argv
from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper


def warn(ledger_name, directories_path):
    print('The following directories will be deleted:')

    for path in directories_path:
        print(str(path))

    print('Deleting a ledger is an irrevocable operation.\nProceed only if you know the consequences.')
    answer = input('Do you want to delete ledger ' + ledger_name + '?\n Press [y/N]')

    if answer.lower() == 'yes' or answer.lower() == 'y':
        return True

    return False


def remove(ledger_name):
    exceptions = ["domain", "config", "pool", "audit"]
    if ledger_name not in exceptions:
        directories_path = []

        for path in Path(config_helper.ledger_data_dir).rglob(ledger_name + "_*"):
            directories_path.append(path)

        if not len(directories_path):
            print('Ledger doesn`t exist: ' + ledger_name)

        elif warn(ledger_name, directories_path):
            for path in directories_path:
                shutil.rmtree(str(path))
            print('Ledger removed successfully!')

    else:
        print('Can`t delete built in ledger: ' + ledger_name)


if __name__ == '__main__':
    config = getConfig()
    config_helper = ConfigHelper(config)
    script, ledger_name = argv
    remove(ledger_name)
