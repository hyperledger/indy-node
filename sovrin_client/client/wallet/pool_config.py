from stp_core.types import Identifier
from plenum.common.constants import TXN_TYPE, FORCE
from sovrin_common.generates_request import GeneratesRequest
from sovrin_common.constants import POOL_CONFIG, WRITES
from sovrin_common.types import Request


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
            return Request(identifier=self.trustee, operation=self._op())
