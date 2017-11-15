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

from enum import unique, IntEnum
from typing import Optional, TypeVar

from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ORIGIN, CURRENT_PROTOCOL_VERSION
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

    def _op(self):
        op = {
            TXN_TYPE: ATTRIB
        }
        if self.dest:
            op[TARGET_NYM] = self.dest
        if self.ledgerStore == LedgerStore.RAW:
            op[RAW] = self.value
        elif self.ledgerStore == LedgerStore.ENC:
            raise NotImplementedError
        elif self.ledgerStore == LedgerStore.HASH:
            raise NotImplementedError
        elif self.ledgerStore == LedgerStore.DONT:
            raise RuntimeError("This attribute cannot be stored externally")
        else:
            raise RuntimeError("Unknown ledgerStore: {}".
                               format(self.ledgerStore))
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
            RAW: self.name
        }
        if self.origin:
            op[ORIGIN] = self.origin
        return op

    def getRequest(self, requestAuthor: Identifier):
        if not self.seqNo:
            return Request(identifier=requestAuthor,
                           operation=self._opForGet(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
