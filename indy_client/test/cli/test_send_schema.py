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

from indy_client.test.cli.constants import SCHEMA_ADDED


def testSendSchemaMultipleAttribs(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)


def testSendSchemaOneAttrib(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree2 version=1.1 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)
