import os
from time import sleep

import pytest
from plenum.cli.cli import Exit, Cli
from plenum.cli.constants import NO_ENV
from plenum.common.util import createDirIfNotExists, normalizedWalletFileName, \
    getWalletFilePath
from plenum.test.cli.helper import checkWalletFilePersisted, checkWalletRestored, \
    createAndAssertNewCreation, createAndAssertNewKeyringCreation, \
    useAndAssertKeyring, exitFromCli, restartCliAndAssert

from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.cli.helper import prompt_is


def performExit(do):
    with pytest.raises(Exit):
        do('exit', within=3)


def testPersistentWalletName():
    # Connects to "test" environment
    walletFileName = normalizedWalletFileName("test")
    assert "test.wallet" == walletFileName
    assert "test" == Cli.getWalletKeyName(walletFileName)

    # New default wallet (keyring) gets created
    walletFileName = normalizedWalletFileName("Default")
    assert "default.wallet" == walletFileName
    assert "default" == Cli.getWalletKeyName(walletFileName)

    # User creates new wallet (keyring)
    walletFileName = normalizedWalletFileName("MyVault")
    assert "myvault.wallet" == walletFileName
    assert "myvault" == Cli.getWalletKeyName(walletFileName)


def getActiveWalletFilePath(cli):
    fileName = cli.getActiveWalletPersitentFileName()
    return getWalletFilePath(cli.getContextBasedKeyringsBaseDir(), fileName)


def _connectTo(envName, do, cli):
    do('connect {}'.format(envName), within=10,
       expect=["Connected to {}".format(envName)])
    prompt_is("{}@{}".format(cli.name, envName))


def connectTo(envName, do, cli, activeWalletPresents, identifiers,
              firstTimeConnect=False):
    currActiveWallet = cli._activeWallet
    _connectTo(envName, do, cli)
    if currActiveWallet is None and firstTimeConnect:
        do(None, expect=[
            "New keyring Default created",
            'Active keyring set to "Default"']
        )

    if activeWalletPresents:
        assert cli._activeWallet is not None
        assert len(cli._activeWallet.identifiers) == identifiers
    else:
        assert cli._activeWallet is None


def switchEnv(newEnvName, do, cli, checkIfWalletRestored=False,
              restoredWalletKeyName=None, restoredIdentifiers=0):
    walletFilePath = getActiveWalletFilePath(cli)
    _connectTo(newEnvName, do, cli)

    # check wallet should have been persisted
    checkWalletFilePersisted(walletFilePath)

    if checkIfWalletRestored:
        checkWalletRestored(cli, restoredWalletKeyName, restoredIdentifiers)


def restartCli(cli, be, do, expectedRestoredWalletName,
               expectedIdentifiers):
    be(cli)
    _connectTo("pool1", do, cli)
    restartCliAndAssert(cli, do, expectedRestoredWalletName, expectedIdentifiers)


def restartCliWithCorruptedWalletFile(cli, be, do, filePath):
    with open(filePath, "a") as myfile:
        myfile.write("appended text to corrupt wallet file")

    be(cli)
    _connectTo("pool1", do, cli)
    do(None,
       expect=[
           'error occurred while restoring wallet',
           'New keyring Default_',
           'Active keyring set to "Default_',
       ],
       not_expect=[
           'Saved keyring "Default" restored',
           'New keyring Default created',
           'Active keyring set to "Default"'
    ], within=5)


def createNewKey(do, cli, keyringName):
    createAndAssertNewCreation(do, cli, keyringName)


def createNewKeyring(name, do, expectedMsgs=None):
    createAndAssertNewKeyringCreation(do, name, expectedMsgs)


def useKeyring(name, do, expectedName=None, expectedMsgs=None):
    useAndAssertKeyring(do, name, expectedName, expectedMsgs)


def testSaveAndRestoreWallet(do, be, cliForMultiNodePools,
                             aliceMultiNodePools,
                             earlMultiNodePools):
    be(cliForMultiNodePools)
    # No wallet should have been restored
    assert cliForMultiNodePools._activeWallet is None

    connectTo("pool1", do, cliForMultiNodePools,
              activeWalletPresents=True, identifiers=0, firstTimeConnect=True)
    createNewKey(do, cliForMultiNodePools, keyringName="Default")

    switchEnv("pool2", do, cliForMultiNodePools, checkIfWalletRestored=False)
    createNewKey(do, cliForMultiNodePools, keyringName="Default")
    createNewKeyring("mykr0", do)
    createNewKey(do, cliForMultiNodePools, keyringName="mykr0")
    createNewKey(do, cliForMultiNodePools, keyringName="mykr0")
    useKeyring("Default", do)
    createNewKey(do, cliForMultiNodePools, keyringName="Default")
    sleep(10)
    switchEnv("pool1", do, cliForMultiNodePools, checkIfWalletRestored=True,
              restoredWalletKeyName="Default", restoredIdentifiers=1)
    createNewKeyring("mykr1", do)
    createNewKey(do, cliForMultiNodePools, keyringName="mykr1")

    switchEnv("pool2", do, cliForMultiNodePools, checkIfWalletRestored=True,
              restoredWalletKeyName="Default", restoredIdentifiers=2)
    createNewKeyring("mykr0", do,
                     expectedMsgs = [
                         '"mykr0" conflicts with an existing keyring',
                         'Please choose a new name.'])

    filePath = getWalletFilePath(cliForMultiNodePools.getContextBasedKeyringsBaseDir(),
                                     cliForMultiNodePools.walletFileName)
    switchEnv("pool1", do, cliForMultiNodePools, checkIfWalletRestored=True,
              restoredWalletKeyName="mykr1", restoredIdentifiers=1)
    useKeyring(filePath, do, expectedName="mykr0",
               expectedMsgs=[
                   "Given wallet file ({}) doesn't "
                   "belong to current context.".format(filePath),
                   "Please connect to 'pool2' environment and try again."])

    # exit from current cli so that active wallet gets saved
    exitFromCli(do)

    # different tests for restoring saved wallet
    filePath = getWalletFilePath(cliForMultiNodePools.getContextBasedKeyringsBaseDir(),
                                     cliForMultiNodePools.walletFileName)
    restartCli(aliceMultiNodePools, be, do, "mykr1", 1)
    restartCliWithCorruptedWalletFile(earlMultiNodePools, be, do, filePath)


def testRestoreWalletFile(aliceCLI):
    import shutil
    fileName = "tmp_wallet_restore_issue"
    curPath = os.path.dirname(os.path.realpath(__file__))
    walletFilePath = os.path.join(curPath, fileName)
    noEnvKeyringsDir = os.path.join(aliceCLI.getKeyringsBaseDir(), NO_ENV)
    createDirIfNotExists(noEnvKeyringsDir)
    shutil.copy2(walletFilePath, noEnvKeyringsDir)
    targetWalletFilePath = os.path.join(noEnvKeyringsDir, fileName)
    restored = aliceCLI.restoreWalletByPath(targetWalletFilePath)
    assert restored and isinstance(aliceCLI.activeWallet, Wallet)
