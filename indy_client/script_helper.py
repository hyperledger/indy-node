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
