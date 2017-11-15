import os

from plenum.common.util import randomString
from indy_client.script_helper import performIndyBaseDirCleanup, \
    keepFilesInClientReset
from indy_client.test.cli.conftest import aliceCLI, CliBuilder, cliTempLogger


def createRandomDirsAndFiles(baseDir):
    dirsCreated = []
    filesCreated = []

    def create(path, file=False, dir=False):
        if not os.path.exists(path):
            if dir:
                os.mkdir(path)
                dirsCreated.append(path)
            elif file:
                with open(path, 'w+') as f:
                    f.write(randomString(20))
                filesCreated.append(path)

    for n in range(1, 10):
        path = os.path.join(baseDir, randomString(5))
        if n % 2 == 0:
            create(path, file=True, dir=False)
        else:
            create(path, file=False, dir=True)

    return dirsCreated, filesCreated


def getCurrentDirAndFiles(baseDir):
    dirs = []
    files = []
    for name in os.listdir(baseDir):
        path = os.path.join(baseDir, name)
        if os.path.isdir(name):
            dirs.append(path)
        else:
            files.append(name)
    return dirs, files


def testResetClient(tconf, aliceCLI):
    newDirs, newFiels = createRandomDirsAndFiles(tconf.CLI_BASE_DIR)
    beforeCleanupDirs, beforeCleanupFiles = getCurrentDirAndFiles(
        tconf.CLI_BASE_DIR)
    backupDir = performIndyBaseDirCleanup(tconf.CLI_BASE_DIR)
    afterCleanupDirs, afterCleanupFiles = getCurrentDirAndFiles(tconf.CLI_BASE_DIR)
    backedupDirs, backedupFiles = getCurrentDirAndFiles(backupDir)
    for name in os.listdir(tconf.CLI_BASE_DIR):
        assert name in keepFilesInClientReset

    assert newDirs not in afterCleanupDirs
    assert newFiels not in afterCleanupFiles

    assert beforeCleanupDirs == backedupDirs
    assert beforeCleanupFiles == backedupFiles
