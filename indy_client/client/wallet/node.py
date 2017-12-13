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
