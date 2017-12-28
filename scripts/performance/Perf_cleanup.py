#! /usr/bin/env python3
import shutil
import os


def close_wallet_and_pool():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """

    print("\n\tCheck if the wallet and pool for this test already exist and delete them...\n")
    x = os.path.expanduser('~')
    work_dir = x + os.sep + ".indy_client"

    try:
        shutil.rmtree(work_dir + "/pool/testPool")
    except IOError as E:
        print(str(E))

    try:
        shutil.rmtree(work_dir + "/wallet/add_nyms_wallet")
    except IOError as E:
        print(str(E))

    print("Finished deleting wallet and pool folders in " + repr(work_dir))
