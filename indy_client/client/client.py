import json
import uuid
from collections import deque
from typing import Dict, Union, Tuple, Optional, Callable

from base58 import b58decode, b58encode
from plenum import config

from plenum.client.client import Client as PlenumClient
from plenum.common.error import fault
from stp_core.common.log import getlogger
from plenum.common.startable import Status

from plenum.common.constants import REPLY, NAME, VERSION, REQACK, REQNACK, \
    TXN_ID, TARGET_NYM, NONCE, STEWARD, OP_FIELD_NAME, REJECT, TYPE
from plenum.common.types import f
from plenum.common.util import libnacl
from plenum.server.router import Router
from stp_core.network.auth_mode import AuthMode
from stp_raet.rstack import SimpleRStack
from stp_zmq.simple_zstack import SimpleZStack

from indy_common.constants import TXN_TYPE, ATTRIB, DATA, GET_NYM, ROLE, \
    NYM, GET_TXNS, LAST_TXN, TXNS, SCHEMA, CLAIM_DEF, SKEY, DISCLO, \
    GET_ATTR, TRUST_ANCHOR, GET_CLAIM_DEF, GET_SCHEMA, SIGNATURE_TYPE, REF

from indy_client.persistence.client_req_rep_store_file import ClientReqRepStoreFile
from indy_client.persistence.client_txn_log import ClientTxnLog
from indy_common.config_util import getConfig
from stp_core.types import HA
from indy_common.state import domain

logger = getlogger()


class Client(PlenumClient):
    def __init__(self,
                 name: str=None,
                 nodeReg: Dict[str, HA]=None,
                 ha: Union[HA, Tuple[str, int]]=None,
                 peerHA: Union[HA, Tuple[str, int]]=None,
                 basedirpath: str=None,
                 config=None,
                 sighex: str=None):
        config = config or getConfig()
        super().__init__(name,
                         nodeReg,
                         ha,
                         basedirpath,
                         config,
                         sighex)
        self.autoDiscloseAttributes = False
        self.requestedPendingTxns = False
        self.hasAnonCreds = bool(peerHA)
        if self.hasAnonCreds:
            self.peerHA = peerHA if isinstance(peerHA, HA) else HA(*peerHA)

            stackargs = dict(name=self.stackName,
                             ha=peerHA,
                             main=True,
                             auth_mode=AuthMode.ALLOW_ANY.value)

            self.peerMsgRoutes = []
            self.peerMsgRouter = Router(*self.peerMsgRoutes)
            self.peerStack = self.peerStackClass(
                stackargs, msgHandler=self.handlePeerMessage)
            self.peerStack.sign = self.sign
            self.peerInbox = deque()
        self._observers = {}  # type Dict[str, Callable]
        self._observerSet = set()  # makes it easier to guard against duplicates

        # To let client send this transactions to just one node
        self._read_only_requests = {GET_NYM,
                                    GET_ATTR,
                                    GET_CLAIM_DEF,
                                    GET_SCHEMA}

    @property
    def peerStackClass(self):
        if config.UseZStack:
            return SimpleZStack
        return SimpleRStack

    def handlePeerMessage(self, msg):
        """
        Use the peerMsgRouter to pass the messages to the correct
         function that handles them

        :param msg: the P2P client message.
        """
        return self.peerMsgRouter.handle(msg)

    def getReqRepStore(self):
        return ClientReqRepStoreFile(self.name, self.basedirpath)

    def getTxnLogStore(self):
        return ClientTxnLog(self.name, self.basedirpath)

    def handleOneNodeMsg(self, wrappedMsg, excludeFromCli=None) -> None:
        msg, sender = wrappedMsg
        # excludeGetTxns = (msg.get(OP_FIELD_NAME) == REPLY and
        #                   msg[f.RESULT.nm].get(TXN_TYPE) == GET_TXNS)
        excludeReqAcks = msg.get(OP_FIELD_NAME) == REQACK
        excludeReqNacks = msg.get(OP_FIELD_NAME) == REQNACK
        excludeReply = msg.get(OP_FIELD_NAME) == REPLY
        excludeReject = msg.get(OP_FIELD_NAME) == REJECT
        excludeFromCli = excludeFromCli or excludeReqAcks or excludeReqNacks \
            or excludeReply or excludeReject
        super().handleOneNodeMsg(wrappedMsg, excludeFromCli)
        if OP_FIELD_NAME not in msg:
            logger.error("Op absent in message {}".format(msg))

    def postReplyRecvd(self, identifier, reqId, frm, result, numReplies):
        reply = super().postReplyRecvd(identifier, reqId, frm, result, numReplies)
        if reply:
            for name in self._observers:
                try:
                    self._observers[name](name, reqId, frm, result, numReplies)
                except Exception as ex:
                    # TODO: All errors should not be shown on CLI, or maybe we
                    # show errors with different color according to the
                    # severity. Like an error occurring due to node sending
                    # a malformed message should not result in an error message
                    # being shown on the cli since the clients would anyway
                    # collect enough replies from other nodes.
                    logger.debug("Observer threw an exception", exc_info=ex)

    def requestConfirmed(self, identifier: str, reqId: int) -> bool:
        return self.txnLog.hasTxnWithReqId(identifier, reqId)

    def hasConsensus(self, identifier: str, reqId: int) -> Optional[str]:
        return super().hasConsensus(identifier, reqId)

    def prepare_for_state(self, result):
        request_type = result[TYPE]
        if request_type == GET_NYM:
            return domain.prepare_get_nym_for_state(result)
        if request_type == GET_ATTR:
            path, value, hashed_value, value_bytes = \
                domain.prepare_get_attr_for_state(result)
            return path, value_bytes
        if request_type == GET_CLAIM_DEF:
            return domain.prepare_get_claim_def_for_state(result)
        if request_type == GET_SCHEMA:
            return domain.prepare_get_schema_for_state(result)
        raise ValueError("Cannot make state key for "
                         "request of type {}"
                         .format(request_type))

    def getTxnsByType(self, txnType):
        return self.txnLog.getTxnsByType(txnType)

    # TODO: Just for now. Remove it later
    def doAttrDisclose(self, origin, target, txnId, key):
        box = libnacl.public.Box(b58decode(origin), b58decode(target))

        data = json.dumps({TXN_ID: txnId, SKEY: key})
        nonce, boxedMsg = box.encrypt(data.encode(), pack_nonce=False)

        op = {
            TARGET_NYM: target,
            TXN_TYPE: DISCLO,
            NONCE: b58encode(nonce),
            DATA: b58encode(boxedMsg)
        }
        self.submit(op, identifier=origin)

    def doGetAttributeTxn(self, identifier, attrName):
        op = {
            TARGET_NYM: identifier,
            TXN_TYPE: GET_ATTR,
            DATA: json.dumps({"name": attrName})
        }
        self.submit(op, identifier=identifier)

    @staticmethod
    def _getDecryptedData(encData, key):
        data = bytes(bytearray.fromhex(encData))
        rawKey = bytes(bytearray.fromhex(key))
        box = libnacl.secret.SecretBox(rawKey)
        decData = box.decrypt(data).decode()
        return json.loads(decData)

    def hasNym(self, nym):
        for txn in self.txnLog.getTxnsByType(NYM):
            if txn.get(TXN_TYPE) == NYM:
                return True
        return False

    def _statusChanged(self, old, new):
        super()._statusChanged(old, new)

    def start(self, loop):
        super().start(loop)
        if self.hasAnonCreds and self.status not in Status.going():
            self.peerStack.start()

    async def prod(self, limit) -> int:
        s = await super().prod(limit)
        if self.hasAnonCreds:
            return s + await self.peerStack.service(limit)
        else:
            return s

    def registerObserver(self, observer: Callable, name=None):
        if not name:
            name = uuid.uuid4()
        if name in self._observers or observer in self._observerSet:
            raise RuntimeError("Observer {} already registered".format(name))
        self._observers[name] = observer
        self._observerSet.add(observer)

    def deregisterObserver(self, name):
        if name not in self._observers:
            raise RuntimeError("Observer {} not registered".format(name))
        self._observerSet.remove(self._observers[name])
        del self._observers[name]

    def hasObserver(self, name):
        return name in self._observerSet
