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

from plenum.test.test_stack import StackedTester, TestStack
from plenum.test.testable import spyable
from indy_client.client.client import Client

from indy_common.test.helper import TempStorage

from indy_common.config_util import getConfig

from stp_core.common.log import getlogger
logger = getlogger()


class TestClientStorage(TempStorage):
    def __init__(self, name, baseDir):
        self.name = name
        self.baseDir = baseDir

    def cleanupDataLocation(self):
        self.cleanupDirectory(self.dataLocation)


@spyable(methods=[Client.handleOneNodeMsg])
class TestClient(Client, StackedTester, TestClientStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TestClientStorage.__init__(self, self.name, self.basedirpath)

    @staticmethod
    def stackType():
        return TestStack

    def onStopping(self, *args, **kwargs):
        # TODO: Why we needed following line?
        # self.cleanupDataLocation()
        super().onStopping(*args, **kwargs)
