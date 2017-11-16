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

from stp_core.types import Identifier
from plenum.common.constants import TXN_TYPE, FORCE, CURRENT_PROTOCOL_VERSION
from indy_common.generates_request import GeneratesRequest
from indy_common.constants import POOL_CONFIG, WRITES
from indy_common.types import Request


class PoolConfig(GeneratesRequest):
    def __init__(self, trustee: Identifier, writes=True, force=False):
        self.trustee = trustee
        self.writes = writes
        self.force = force
        self.seqNo = None

    def _op(self):
        op = {
            TXN_TYPE: POOL_CONFIG,
            WRITES: self.writes,
            FORCE: self.force
        }
        return op

    @property
    def key(self):
        return '.'.join([str(self.writes), str(self.force)])

    def ledgerRequest(self):
        if not self.seqNo:
            return Request(identifier=self.trustee,
                           operation=self._op(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
