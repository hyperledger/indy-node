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
import functools
import shutil

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, composeUpgradeMessage, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from indy_node.server.upgrader import Upgrader

m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlRestoresFromBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()
    backupWasRestored = m.Value('b', False)
    testFile = 'testFile'
    original_text = '1'
    new_text = '2'

    def testRestoreBackup(tool, version):
        tool._restore_from_backup_test(version)
        backupWasRestored.value = True

    def mockMigrate(tool, *args):
        monkeypatch.setattr(tool, '_migrate', lambda *args: None)
        with open(os.path.join(tool.indy_dir, testFile), 'w') as f:
            f.write(new_text)
        raise Exception('test')

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._restore_from_backup_test = tool._restore_from_backup
        monkeypatch.setattr(
            tool, '_migrate', functools.partial(mockMigrate, tool))
        monkeypatch.setattr(tool, '_restore_from_backup',
                            functools.partial(testRestoreBackup, tool))

    def checkBackupRestored(tool):
        assert backupWasRestored.value

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        with open(os.path.join(nct.tool.indy_dir, testFile), 'w') as f:
            f.write(original_text)
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackupRestored, nct.tool))
        with open(os.path.join(nct.tool.indy_dir, testFile)) as f:
            assert original_text == f.read()
    finally:
        clean_dir(nct.tool.base_dir)
        nct.stop()


def clean_dir(dir):
    for file in os.listdir(dir):
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file, ignore_errors=True)