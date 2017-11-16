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
import shutil

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from indy_node.server.upgrader import Upgrader

m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlCreatesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_remove_old_backups', lambda *x: None)

    def checkBackup(tool):
        assert os.path.isfile('{}.{}'.format(
            tool._backup_name(currentVersion), tool.backup_format))

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackup, nct.tool))
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