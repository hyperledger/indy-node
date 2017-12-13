import os
import shutil

from plenum.common.util import randomString

keepFilesInClientReset = [
    'pool_transactions_sandbox',
    'indy_config.py',
    'sample',
    'pool_transactions_local',
    'pool_transactions_live'
]


def performIndyBaseDirCleanup(baseDir):
    backupDir = None
    while True:
        backupDir = baseDir + "-" + randomString(6)
        if not os.path.exists(backupDir):
            shutil.copytree(baseDir, backupDir)
            print("\nIndy base directory {} backed up at: {}".
                  format(baseDir, backupDir))
            break

    for filename in os.listdir(baseDir):
        filepath = os.path.join(baseDir, filename)
        if filename not in keepFilesInClientReset:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
    return backupDir
