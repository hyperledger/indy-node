import json
import os
from collections import deque
from copy import deepcopy
from hashlib import sha256
from typing import Iterable, Any, List

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.serializers.compact_serializer import CompactSerializer
from ledger.stores.file_hash_store import FileHashStore
from ledger.serializers.json_serializer import JsonSerializer

from plenum.common.exceptions import InvalidClientRequest
from plenum.persistence.util import txnsWithMerkleInfo
from sovrin_node.persistence.attribute_store import AttributeStore
from stp_core.common.log import getlogger
from plenum.common.constants import NAME, VERSION, ORIGIN, \
    POOL_TXN_TYPES, NODE_PRIMARY_STORAGE_SUFFIX, TXN_TYPE, TARGET_NYM, \
    DATA, HASH, ENC, RAW, DOMAIN_LEDGER_ID, POOL_LEDGER_ID
from plenum.common.types import Reply, RequestAck, f, \
    OPERATION, LedgerStatus
from plenum.common.util import error

from plenum.persistence.storage import initStorage
from plenum.server.node import Node as PlenumNode
from plenum.common.ledger import Ledger

from plenum.persistence.pruning_state import PruningState


from sovrin_common.config_util import getConfig
from sovrin_common.constants import allOpKeys, ATTRIB, GET_ATTR, \
    GET_NYM, reqOpKeys, GET_TXNS, GET_SCHEMA, \
    GET_ISSUER_KEY, REF, ACTION, NODE_UPGRADE, COMPLETE, FAIL
from sovrin_common.txn_util import getTxnOrderedFields
from sovrin_common.types import Request
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.client_authn import TxnBasedAuthNr
from sovrin_node.server.config_req_handler import ConfigReqHandler
from sovrin_node.server.constants import CONFIG_LEDGER_ID, openTxns, \
    validTxnTypes, IDENTITY_TXN_TYPES, CONFIG_TXN_TYPES
from sovrin_node.server.domain_req_handler import DomainReqHandler
from sovrin_node.server.node_authn import NodeAuthNr
from sovrin_node.server.pool_manager import HasPoolManager
from sovrin_node.server.upgrader import Upgrader

logger = getlogger()
jsonSerz = JsonSerializer()


class Node(PlenumNode, HasPoolManager):
    keygenScript = "init_sovrin_keys"

    def __init__(self,
                 name,
                 nodeRegistry=None,
                 clientAuthNr=None,
                 ha=None,
                 cliname=None,
                 cliha=None,
                 basedirpath=None,
                 primaryDecider=None,
                 pluginPaths: Iterable[str] = None,
                 storage=None,
                 config=None):
        self.config = config or getConfig()

        # TODO: 3 ugly lines ahead, don't know how to avoid
        # self.stateTreeStore = None
        self.idrCache = None
        self.attributeStore = None

        super().__init__(name=name,
                         nodeRegistry=nodeRegistry,
                         clientAuthNr=clientAuthNr,
                         ha=ha,
                         cliname=cliname,
                         cliha=cliha,
                         basedirpath=basedirpath,
                         primaryDecider=primaryDecider,
                         pluginPaths=pluginPaths,
                         storage=storage,
                         config=self.config)
        domainState = self.getState(DOMAIN_LEDGER_ID)
        # self.stateTreeStore = StateTreeStore(domainState)

        # TODO: ugly line ahead, don't know how to avoid
        self.clientAuthNr = clientAuthNr or self.defaultAuthNr()

        self.configLedger = self.getConfigLedger()
        self.ledgerManager.addLedger(CONFIG_LEDGER_ID, self.configLedger,
                                     postCatchupCompleteClbk=self.postConfigLedgerCaughtUp,
                                     postTxnAddedToLedgerClbk=self.postTxnFromCatchupAddedToLedger)
        self.states[CONFIG_LEDGER_ID] = self.loadConfigState()
        self.upgrader = self.getUpgrader()
        self.configReqHandler = self.getConfigReqHandler()
        self.initConfigState()
        for r in self.replicas:
            r.requestQueues[CONFIG_LEDGER_ID] = deque()
        self.requestExecuter[CONFIG_LEDGER_ID] = self.executeConfigTxns

        self.nodeMsgRouter.routes[Request] = self.processNodeRequest
        self.nodeAuthNr = self.defaultNodeAuthNr()

    def initPoolManager(self, nodeRegistry, ha, cliname, cliha):
        HasPoolManager.__init__(self, nodeRegistry, ha, cliname, cliha)

    def getPrimaryStorage(self):
        """
        This is usually an implementation of Ledger
        """
        if self.config.primaryStorage is None:
            fields = getTxnOrderedFields()
            return Ledger(CompactMerkleTree(hashStore=self.hashStore),
                          dataDir=self.dataLocation,
                          serializer=CompactSerializer(fields=fields),
                          fileName=self.config.domainTransactionsFile,
                          ensureDurability=self.config.EnsureLedgerDurability)
        else:
            return initStorage(self.config.primaryStorage,
                               name=self.name + NODE_PRIMARY_STORAGE_SUFFIX,
                               dataDir=self.dataLocation,
                               config=self.config)

    def getUpgrader(self):
        return Upgrader(self.id,
                        self.name,
                        self.dataLocation,
                        self.config,
                        self.configLedger,
                        upgradeFailedCallback=self.postConfigLedgerCaughtUp)

    def getDomainReqHandler(self):
        if self.idrCache is None:
            self.idrCache = IdrCache(self.dataLocation, name=self.name)
        if self.attributeStore is None:
            self.attributeStore = self.loadAttributeStore()
        return DomainReqHandler(self.domainLedger,
                                self.states[DOMAIN_LEDGER_ID],
                                self.reqProcessors,
                                self.idrCache,
                                self.attributeStore
                                )

    def getConfigLedger(self):
        return Ledger(CompactMerkleTree(hashStore=FileHashStore(
            fileNamePrefix='config', dataDir=self.dataLocation)),
            dataDir=self.dataLocation,
            fileName=self.config.configTransactionsFile,
            ensureDurability=self.config.EnsureLedgerDurability)

    def loadConfigState(self):
        return PruningState(os.path.join(self.dataLocation,
                                         self.config.configStateDbName))

    def loadAttributeStore(self):
        dbPath = os.path.join(self.dataLocation, self.config.attrDB)
        return AttributeStore(dbPath)

    def getConfigReqHandler(self):
        return ConfigReqHandler(self.configLedger,
                                self.states[CONFIG_LEDGER_ID],
                                self.idrCache, self.upgrader,
                                self.poolManager)

    def initConfigState(self):
        self.initStateFromLedger(self.states[CONFIG_LEDGER_ID],
                                 self.configLedger, self.configReqHandler)

    def postDomainLedgerCaughtUp(self, **kwargs):
        # TODO: Reconsider, shouldn't config ledger be synced before domain
        # ledger, since processing config ledger can lead to restart and
        # thus rework (running the sync for ledgers again).
        # A counter argument is since domain ledger contains identities and thus
        # trustees, its needs to sync first
        super().postDomainLedgerCaughtUp(**kwargs)
        self.ledgerManager.setLedgerCanSync(CONFIG_LEDGER_ID, True)
        # Node has discovered other nodes now sync up domain ledger
        for nm in self.nodestack.connecteds:
            self.sendConfigLedgerStatus(nm)
        self.ledgerManager.processStashedLedgerStatuses(CONFIG_LEDGER_ID)

    def sendConfigLedgerStatus(self, nodeName):
        self.sendLedgerStatus(nodeName, CONFIG_LEDGER_ID)

    @property
    def configLedgerStatus(self):
        return LedgerStatus(CONFIG_LEDGER_ID, self.configLedger.size,
                            self.configLedger.root_hash)

    def getLedgerStatus(self, ledgerId: int):
        if ledgerId == CONFIG_LEDGER_ID:
            return self.configLedgerStatus
        else:
            return super().getLedgerStatus(ledgerId)

    def postPoolLedgerCaughtUp(self, **kwargs):
        # The only reason to override this is to set the correct node id in
        # the upgrader since when the upgrader is initialized, node might not
        # have its id since it maybe missing the complete pool ledger.
        # TODO: Maybe a cleaner way is to initialize upgrader only when pool
        # ledger has caught up.
        super().postPoolLedgerCaughtUp(**kwargs)
        self.upgrader.nodeId = self.id

    def postConfigLedgerCaughtUp(self, **kwargs):
        if all(r.primaryName is not None for r in self.replicas):
            self.upgrader.processLedger()
            if self.upgrader.isItFirstRunAfterUpgrade:
                lastUpgradeVersion = self.upgrader.lastExecutedUpgradeInfo[1]
                action = COMPLETE if self.upgrader.didLastExecutedUpgradeSucceeded else FAIL
                op = {
                    TXN_TYPE: NODE_UPGRADE,
                    DATA: {
                        ACTION: action,
                        VERSION: lastUpgradeVersion
                    }
                }
                op[f.SIG.nm] = self.wallet.signMsg(op[DATA])
                request = self.wallet.signOp(op)
                self.startedProcessingReq(*request.key, self.nodestack.name)
                self.send(request)
        else:
            self._schedule(self.postConfigLedgerCaughtUp, 3)

    def processNodeRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == NODE_UPGRADE:
            try:
                self.nodeAuthNr.authenticate(request.operation[DATA],
                                             request.identifier,
                                             request.operation[f.SIG.nm])
            except:
                # TODO: Do something here
                return
        if not self.isProcessingReq(*request.key):
            self.startedProcessingReq(*request.key, frm)
        # If not already got the propagate request(PROPAGATE) for the
        # corresponding client request(REQUEST)
        self.recordAndPropagate(request, frm)

    def postTxnFromCatchup(self, ledgerId: int, txn: Any):
        if ledgerId == CONFIG_LEDGER_ID:
            return self.configReqHandler
        else:
            return super().postTxnFromCatchup(ledgerId, txn)

    def validateNodeMsg(self, wrappedMsg):
        msg, frm = wrappedMsg
        if all(attr in msg.keys()
               for attr in [OPERATION, f.IDENTIFIER.nm, f.REQ_ID.nm]) \
                and msg.get(OPERATION, {}).get(TXN_TYPE) == NODE_UPGRADE:
            cls = Request
            cMsg = cls(**msg)
            return cMsg, frm
        else:
            return super().validateNodeMsg(wrappedMsg)

    def authNr(self, req):
        # TODO: Assumption that NODE_UPGRADE can be sent by nodes only
        if req.get(OPERATION, {}).get(TXN_TYPE) == NODE_UPGRADE:
            return self.nodeAuthNr
        else:
            return super().authNr(req)

    def isSignatureVerificationNeeded(self, msg: Any):
        op = msg.get(OPERATION)
        if op:
            if op.get(TXN_TYPE) in openTxns:
                return False
        return True

    def doStaticValidation(self, identifier, reqId, operation):
        super().doStaticValidation(identifier, reqId, operation)
        unknownKeys = set(operation.keys()).difference(set(allOpKeys))
        if unknownKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'invalid keys "{}"'.
                                       format(",".join(unknownKeys)))

        missingKeys = set(reqOpKeys).difference(set(operation.keys()))
        if missingKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'missing required keys "{}"'.
                                       format(",".join(missingKeys)))

        if operation[TXN_TYPE] not in validTxnTypes:
            raise InvalidClientRequest(identifier, reqId, 'invalid {}: {}'.
                                       format(TXN_TYPE, operation[TXN_TYPE]))

        typ = operation.get(TXN_TYPE)
        ledgerId = self.ledgerId(typ)
        if ledgerId == DOMAIN_LEDGER_ID:
            self.reqHandler.doStaticValidation(identifier, reqId,
                                               operation)
            return
        if ledgerId == CONFIG_LEDGER_ID:
            self.configReqHandler.doStaticValidation(identifier, reqId,
                                                     operation)

    def doDynamicValidation(self, request: Request):
        """
        State based validation
        """
        if self.ledgerIdForRequest(request) == CONFIG_LEDGER_ID:
            self.configReqHandler.validate(request, self.config)
        else:
            super().doDynamicValidation(request)

    def defaultAuthNr(self):
        return TxnBasedAuthNr(self.idrCache)

    def defaultNodeAuthNr(self):
        return NodeAuthNr(self.poolLedger)

    async def prod(self, limit: int = None) -> int:
        c = await super().prod(limit)
        c += self.upgrader.service()
        return c

    def processGetSchemaReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        authorDid = request.operation[TARGET_NYM]
        schema, lastSeqNo = self.reqHandler.getSchema(
            author=authorDid,
            schemaName=(request.operation[DATA][NAME]),
            schemaVersion=(request.operation[DATA][VERSION])
        )
        schema.update({ORIGIN: authorDid})
        result = {**request.operation, **{
            DATA: schema,
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
            f.SEQ_NO.nm: lastSeqNo
        }}
        self.transmitToClient(Reply(result), frm)

    def processGetAttrsReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        attrName = request.operation[RAW]
        nym = request.operation[TARGET_NYM]
        attrValue, lastSeqNo = \
            self.reqHandler.getAttr(did=nym, key=attrName)
        result = {**request.operation, **{
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
        }}
        if attrValue is not None:
            attr = json.dumps({attrName: attrValue}, sort_keys=True)
            result[DATA] = attr
            result[f.SEQ_NO.nm] = lastSeqNo
        self.transmitToClient(Reply(result), frm)

    def processGetIssuerKeyReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        keys, lastSeqNo = self.reqHandler.getIssuerKey(
            author=request.operation[ORIGIN],
            schemaSeqNo=request.operation[REF]
        )
        result = {**request.operation, **{
            DATA: keys,
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
            f.SEQ_NO.nm: lastSeqNo
        }}
        self.transmitToClient(Reply(result), frm)

    def processRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == GET_NYM:
            self.transmitToClient(RequestAck(*request.key), frm)
            result = self.reqHandler.handleGetNymReq(request, frm)
            self.transmitToClient(Reply(result), frm)
        # TODO: Come back to it
        elif request.operation[TXN_TYPE] == GET_TXNS:
            # self.processGetTxnReq(request, frm)
            return
        elif request.operation[TXN_TYPE] == GET_SCHEMA:
            self.processGetSchemaReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_ATTR:
            self.processGetAttrsReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_ISSUER_KEY:
            self.processGetIssuerKeyReq(request, frm)
        else:
            super().processRequest(request, frm)

    @classmethod
    def ledgerId(cls, txnType: str):
        if txnType in POOL_TXN_TYPES:
            return POOL_LEDGER_ID
        if txnType in IDENTITY_TXN_TYPES:
            return DOMAIN_LEDGER_ID
        if txnType in CONFIG_TXN_TYPES:
            return CONFIG_LEDGER_ID

    def applyReq(self, request: Request):
        """
        Apply request to appropriate ledger and state
        """
        if self.__class__.ledgerIdForRequest(request) == CONFIG_LEDGER_ID:
            return self.configReqHandler.apply(request)
        else:
            return super().applyReq(request)

    @staticmethod
    def hashAttribTxn(result):
        # Creating copy of result so that `RAW`, `ENC` or `HASH` can be
        # replaced by their hashes. We do not insert actual attribute data
        # in the ledger but only the hash of it.
        result = deepcopy(result)
        if RAW in result:
            result[RAW] = sha256(result[RAW].encode()).hexdigest()
            # TODO: add checking for a number of keys in json
        elif ENC in result:
            result[ENC] = sha256(result[ENC].encode()).hexdigest()
        elif HASH in result:
            result[HASH] = result[HASH]
        else:
            error("Transaction missing required field")
        return result

    def getReplyFor(self, request):
        typ = request.operation.get(TXN_TYPE)
        if typ in IDENTITY_TXN_TYPES:
            reply = self.getReplyFromLedger(self.domainLedger, request)
            if reply:
                if request.operation[TXN_TYPE] == ATTRIB:
                    result = self.hashAttribTxn(reply.result)
                    reply = Reply(result)
                return reply
            else:
                return None
        if typ in CONFIG_TXN_TYPES:
            return self.getReplyFromLedger(self.configLedger, request)

    def commitAndUpdate(self, reqHandler, ppTime, reqs: List[Request],
                       stateRoot, txnRoot) -> List:
        committedTxns = reqHandler.commit(len(reqs), stateRoot, txnRoot)
        self.updateSeqNoMap(committedTxns)
        committedTxns = txnsWithMerkleInfo(reqHandler.ledger,
                                           committedTxns)
        self.sendRepliesToClients(committedTxns, ppTime)
        return committedTxns

    def executeDomainTxns(self, ppTime, reqs: List[Request], stateRoot,
                          txnRoot) -> List:
        """
        Execute the REQUEST sent to this Node

        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST
        """
        return self.commitAndUpdate(self.reqHandler, ppTime, reqs, stateRoot,
                                    txnRoot)

    def executeConfigTxns(self, ppTime, reqs: List[Request], stateRoot,
                          txnRoot) -> List:
        return self.commitAndUpdate(self.configReqHandler, ppTime, reqs,
                                    stateRoot, txnRoot)

    def closeAllKVStores(self):
        super().closeAllKVStores()
        if self.idrCache:
            self.idrCache.close()
        if self.attributeStore:
            self.attributeStore.close()

    def onBatchCreated(self, ledgerId, stateRoot):
        if ledgerId == CONFIG_LEDGER_ID:
            self.configReqHandler.onBatchCreated(stateRoot)
        else:
            super().onBatchCreated(ledgerId, stateRoot)

    def onBatchRejected(self, ledgerId, stateRoot=None):
        if ledgerId == CONFIG_LEDGER_ID:
            self.configReqHandler.onBatchRejected(stateRoot)
        else:
            super().onBatchRejected(ledgerId, stateRoot)
