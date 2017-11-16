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

import multiprocessing
import os

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, sendUpgradeMessage, nodeControlGeneralMonkeypatching



m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlPerformsMigrations(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    migrationFile = 'migrationProof'
    migrationText = 'testMigrations'

    def mock_migrate(*args):
        with open(os.path.join(tdir, migrationFile), 'w') as f:
            f.write(migrationText)

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_migrate', mock_migrate)

    def checkMigration():
        with open(os.path.join(tdir, migrationFile)) as f:
            assert f.read() == migrationText

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkMigration))
    finally:
        nct.stop()