import shutil
import os


def delete_wallets_and_pools():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """

    print("\nCheck if the wallet and pool for this test already exist and delete them...\n")

    user_home = os.path.expanduser('~') + os.sep
    work_dir = user_home + ".indy_client"

    try:
        shutil.rmtree(work_dir + "/pool/")
    except IOError as E:
        print(str(E))

    try:
        shutil.rmtree(work_dir + "/wallet/")
    except IOError as E:
        print(str(E))

    print("Finished deleting wallet and pool folders in " + repr(work_dir))


if __name__ == '__main__':
    delete_wallets_and_pools()
