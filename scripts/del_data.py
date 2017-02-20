#!/usr/bin/env python3

import shutil
import os
import pyorient

client = pyorient.OrientDB("localhost", 2424)
user = "root"
password = "password"
session_id = client.connect(user, password)


def dropdbs():
    i = 0
    names = [n for n in client.db_list().oRecordData['databases'].keys()]
    for nm in names:
        try:
            client.db_drop(nm)
            i += 1
        except:
            continue
    return i


def drop():
    try:
        shutil.rmtree(os.path.join(os.path.expanduser("~"), ".sovrin", "data"))
    except Exception as e:
        print("directory not found {}".format(e))
    return dropdbs()


drop()
