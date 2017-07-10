from stp_core.types import Identifier
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE
from sovrin_common.generates_request import GeneratesRequest
from sovrin_common.constants import POOL_UPGRADE, ACTION, SCHEDULE, \
    SHA256, TIMEOUT, START, JUSTIFICATION
from sovrin_common.types import Request


class Upgrade(GeneratesRequest):
    def __init__(self, name: str, version: str, action: str, sha256: str,
                 trustee: Identifier, schedule: dict=None, timeout=None,
                 justification=None, force=False):
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
                TIMEOUT: self.timeout
            })

        if self.action == START:
            op.update({
                JUSTIFICATION: self.justification
            })
        return op

    @property
    def key(self):
        return '.'.join([self.name, self.version, self.action])

    def ledgerRequest(self):
        if not self.seqNo:
            return Request(identifier=self.trustee, operation=self._op())
