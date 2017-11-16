#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os
import shutil

from plenum.cli.constants import NO_ENV
from plenum.common.util import createDirIfNotExists
from indy_client.client.wallet.wallet import Wallet


def testRestoreWalletFromMinimalGoLive(aliceCLI):
    fileName = "wallet_from_minimal_go_live"
    curPath = os.path.dirname(os.path.realpath(__file__))
    walletFilePath = os.path.join(curPath, fileName)
    noEnvKeyringsDir = os.path.join(aliceCLI.getWalletsBaseDir(), NO_ENV)
    createDirIfNotExists(noEnvKeyringsDir)
    shutil.copy2(walletFilePath, noEnvKeyringsDir)
    targetWalletFilePath = os.path.join(noEnvKeyringsDir, fileName)
    restored = aliceCLI.restoreWalletByPath(targetWalletFilePath)
    assert restored and isinstance(aliceCLI.activeWallet, Wallet)
