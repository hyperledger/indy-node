from enum import unique, IntEnum
from typing import Optional, TypeVar

from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, ORIGIN, CURRENT_PROTOCOL_VERSION
from indy_common.generates_request import GeneratesRequest
from indy_common.constants import ATTRIB, GET_ATTR
from indy_common.types import Request
from stp_core.types import Identifier

Value = TypeVar('Value', str, dict)


class AttributeKey:
    def __init__(self,
                 name: str,
                 origin: Identifier,
                 dest: Optional[Identifier]=None):
        self.name = name
        self.origin = origin
        self.dest = dest

    def key(self):
        return self.name, self.origin, self.dest


@unique
class LedgerStore(IntEnum):
    """
    How to store an attribute on the distributed ledger.

    1. DONT: don't store on public ledger
    2. HASH: store just a hash
    3. ENC: store encrypted
    4. RAW: store in plain text
    """
    DONT = 1
    HASH = 2
    ENC = 3
    RAW = 4

    @property
    def isWriting(self) -> bool:
        """
        Return whether this transaction needs to be written
        """
        return self != self.DONT


class Attribute(AttributeKey, GeneratesRequest):
    # TODO we want to store a history of the attribute changes
    def __init__(self,
                 name: str,  # local human friendly name
                 value: Value=None,     # None when we gt the attribute
                 origin: Identifier=None,  # authoring of the attribute
                 dest: Optional[Identifier]=None,  # target
                 ledgerStore: LedgerStore=LedgerStore.DONT,
                 encKey: Optional[str]=None,  # encryption key
                 seqNo: Optional[int]=None):  # ledger sequence number
        super().__init__(name, origin, dest)
        self.value = value
        self.ledgerStore = ledgerStore
        self.encKey = encKey
        self.seqNo = seqNo

    def _op_fill_attr_type_and_data(self, op, data):
        if self.ledgerStore == LedgerStore.RAW:
            op[RAW] = data
        elif self.ledgerStore == LedgerStore.ENC:
            op[ENC] = data
        elif self.ledgerStore == LedgerStore.HASH:
            op[HASH] = data
        elif self.ledgerStore == LedgerStore.DONT:
            raise RuntimeError("This attribute cannot be stored externally")
        else:
            raise RuntimeError("Unknown ledgerStore: {}".
                               format(self.ledgerStore))

    def _op(self):
        op = {
            TXN_TYPE: ATTRIB
        }
        if self.dest:
            op[TARGET_NYM] = self.dest
        self._op_fill_attr_type_and_data(op, self.value)

        return op

    def ledgerRequest(self):
        if self.ledgerStore.isWriting and not self.seqNo:
            assert self.origin is not None
            return Request(identifier=self.origin,
                           operation=self._op(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)

    def _opForGet(self):
        op = {
            TARGET_NYM: self.dest,
            TXN_TYPE: GET_ATTR,
        }
        self._op_fill_attr_type_and_data(op, self.name)
        if self.origin:
            op[ORIGIN] = self.origin
        return op

    def getRequest(self, requestAuthor: Identifier):
        if not self.seqNo:
            return Request(identifier=requestAuthor,
                           operation=self._opForGet(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
