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

from plenum.common.constants import TXN_TYPE, TARGET_NYM, NODE, DATA, CURRENT_PROTOCOL_VERSION
from indy_common.generates_request import GeneratesRequest
from indy_common.types import Request
from stp_core.types import Identifier


class Node(GeneratesRequest):
    def __init__(self, id: Identifier, data: dict, steward: Identifier):
        self.id = id
        self.data = data
        self.steward = steward
        self.seqNo = None

    def _op(self):
        op = {
            TXN_TYPE: NODE,
            TARGET_NYM: self.id,
            DATA: self.data
        }
        return op

    def ledgerRequest(self):
        if not self.seqNo:
            assert self.id is not None
            return Request(identifier=self.steward,
                           operation=self._op(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
