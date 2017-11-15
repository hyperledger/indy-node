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
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE, CURRENT_PROTOCOL_VERSION
from indy_common.generates_request import GeneratesRequest
from indy_common.constants import POOL_UPGRADE, ACTION, SCHEDULE, \
    SHA256, TIMEOUT, START, JUSTIFICATION, REINSTALL
from indy_common.types import Request


class Upgrade(GeneratesRequest):
    def __init__(self, name: str, version: str, action: str, sha256: str,
                 trustee: Identifier, schedule: dict=None, timeout=None,
                 justification=None, force=False, reinstall=False):
        self.name = name
        self.version = version
        self.action = action
        self.schedule = schedule
        self.sha256 = sha256
        self.timeout = timeout
        self.justification = justification
        self.trustee = trustee
        self.seqNo = None
        self.force = force
        self.reinstall = reinstall

    def _op(self):
        op = {
            TXN_TYPE: POOL_UPGRADE,
            NAME: self.name,
            VERSION: self.version,
            ACTION: self.action,
            SHA256: self.sha256,
            FORCE: self.force
        }
        if self.action == START:
            op.update({
                SCHEDULE: self.schedule,
                TIMEOUT: self.timeout,
                JUSTIFICATION: self.justification,
                REINSTALL: self.reinstall,
            })

        return op

    @property
    def key(self):
        return '.'.join([self.name, self.version, self.action])

    def ledgerRequest(self):
        if not self.seqNo:
            return Request(identifier=self.trustee,
                           operation=self._op(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
