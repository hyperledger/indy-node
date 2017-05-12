#!/usr/bin/env python3

import shutil
import os
import argparse
import re


def pathList(*paths):
    return {os.path.expanduser(path) for path in paths}


TARGET_DIRS = pathList(
    "~/.sovrin",
    "~/.plenum"
)

PATHS_TO_CLEAR = (
    '/.*/role',
    '/.*/verif_keys',
    '/.*/sig_keys',
    '/.*/public_keys',
    '/.*/private_keys'
)

WHITE_LIST = pathList(
    "~/.sovrin/sovrin_config.py",
    "~/.plenum/plenum_config.py",
    "~/.sovrin/.*log"
).union(pathList(*{d+p for d in TARGET_DIRS for p in PATHS_TO_CLEAR}))


def clean_files(full):
    if full:
        for dir in TARGET_DIRS:
            if os.path.exists(dir):
                shutil.rmtree(dir)
        return

    files_to_keep = [re.compile(pattern) for pattern in WHITE_LIST]

    def isOk(path):
         return any(pattern.match(path) for pattern in files_to_keep)

    for dir in TARGET_DIRS:
        for root, dirs, files in os.walk(dir):
            if not isOk(root):
                for file in files:
                    fullName = os.path.join(root, file)
                    if not isOk(fullName):
                        os.remove(fullName)
                if not os.listdir(root):
                    os.rmdir(root)
            else:
                dirs[:] = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Removes node data and configuration')
    parser.add_argument('--full',
                        action="store_true",
                        help="remove configs and logs too")
    args = parser.parse_args()
    clean_files(args.full)
