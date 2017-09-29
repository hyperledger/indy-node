import os
import shutil

from plenum.cli.constants import NO_ENV
from plenum.common.util import createDirIfNotExists
from indy_client.client.wallet.wallet import Wallet


def testRestoreWalletBeforeRenamingLinkToConnection(aliceCLI):
    fileName = "wallet_before_renaming_link_to_connection"
    curPath = os.path.dirname(os.path.realpath(__file__))
    walletFilePath = os.path.join(curPath, fileName)
    noEnvKeyringsDir = os.path.join(aliceCLI.getWalletsBaseDir(), NO_ENV)
    createDirIfNotExists(noEnvKeyringsDir)
    shutil.copy2(walletFilePath, noEnvKeyringsDir)
    targetWalletFilePath = os.path.join(noEnvKeyringsDir, fileName)
    restored = aliceCLI.restoreWalletByPath(targetWalletFilePath)
    assert restored and isinstance(aliceCLI.activeWallet, Wallet)
