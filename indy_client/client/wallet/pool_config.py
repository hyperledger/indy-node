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
