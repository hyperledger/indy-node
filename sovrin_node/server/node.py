from typing import Iterable, Any, List

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.serializers.compact_serializer import CompactSerializer
from ledger.serializers.json_serializer import JsonSerializer
from ledger.stores.file_hash_store import FileHashStore
from state.pruning_state import PruningState

from plenum.common.constants import VERSION, \
    POOL_TXN_TYPES, NODE_PRIMARY_STORAGE_SUFFIX, \
    ENC, RAW, DOMAIN_LEDGER_ID, POOL_LEDGER_ID, LedgerState
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.ledger import Ledger
from plenum.common.types import f, \
    OPERATION
from plenum.common.messages.node_messages import Reply
from plenum.persistence.storage import initStorage, initKeyValueStorage
from plenum.server.node import Node as PlenumNode
from sovrin_common.config_util import getConfig
from sovrin_common.constants import TXN_TYPE, allOpKeys, ATTRIB, GET_ATTR, \
    DATA, GET_NYM, reqOpKeys, GET_TXNS, GET_SCHEMA, GET_CLAIM_DEF, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, CONFIG_LEDGER_ID, POOL_UPGRADE
from sovrin_common.constants import openTxns, \
    validTxnTypes, IDENTITY_TXN_TYPES, CONFIG_TXN_TYPES
from sovrin_common.txn_util import getTxnOrderedFields
from sovrin_common.types import Request, SafeRequest
from sovrin_node.persistence.attribute_store import AttributeStore
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.client_authn import TxnBasedAuthNr
from sovrin_node.server.config_req_handler import ConfigReqHandler
from sovrin_node.server.domain_req_handler import DomainReqHandler
from sovrin_node.server.node_authn import NodeAuthNr
from sovrin_node.server.pool_manager import HasPoolManager
from sovrin_node.server.upgrader import Upgrader
from stp_core.common.log import getlogger
import os


logger = getlogger()
jsonSerz = JsonSerializer()


class Node(PlenumNode, HasPoolManager):
    keygenScript = "init_sovrin_keys"
    _client_request_class = SafeRequest
    ledger_ids = PlenumNode.ledger_ids + [CONFIG_LEDGER_ID]

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

        # TODO: ugly line ahead, don't know how to avoid
        self.clientAuthNr = clientAuthNr or self.defaultAuthNr()

        self.configLedger = self.getConfigLedger()
        self.ledgerManager.addLedger(CONFIG_LEDGER_ID, self.configLedger,
                                     postCatchupCompleteClbk=self.postConfigLedgerCaughtUp,
                                     postTxnAddedToLedgerClbk=self.postTxnFromCatchupAddedToLedger)
        self.on_new_ledger_added(CONFIG_LEDGER_ID)
        self.states[CONFIG_LEDGER_ID] = self.loadConfigState()
        self.upgrader = self.getUpgrader()
        self.configReqHandler = self.getConfigReqHandler()
        self.initConfigState()
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

            defaultTxnFile = os.path.join(self.basedirpath,
                                          self.config.domainTransactionsFile)
            if not os.path.exists(defaultTxnFile):
                logger.debug("Not using default initialization file for "
                             "domain ledger, since it does not exist: {}"
                             .format(defaultTxnFile))
                defaultTxnFile = None

            return Ledger(CompactMerkleTree(hashStore=self.hashStore),
                          dataDir=self.dataLocation,
                          serializer=CompactSerializer(fields=fields),
                          fileName=self.config.domainTransactionsFile,
                          ensureDurability=self.config.EnsureLedgerDurability,
                          defaultFile=defaultTxnFile)
        else:
            return initStorage(self.config.primaryStorage,
                               name=self.name + NODE_PRIMARY_STORAGE_SUFFIX,
                               dataDir=self.dataLocation,
                               config=self.config)

    def send_ledger_status_to_newly_connected_node(self, node_name):
        super().send_ledger_status_to_newly_connected_node(node_name)
        # If the domain ledger is already synced send config ledger status
        # else after the domain ledger is caught up, config ledger status
        # will be sent
        if self.ledgerManager.ledgerRegistry[DOMAIN_LEDGER_ID].state == LedgerState.synced:
            self.sendConfigLedgerStatus(node_name)

    def getUpgrader(self):
        return Upgrader(self.id,
                        self.name,
                        self.dataLocation,
                        self.config,
                        self.configLedger,
                        upgradeFailedCallback=self.postConfigLedgerCaughtUp)

    def getDomainReqHandler(self):
        if self.idrCache is None:
            self.idrCache = self.getIdrCache()
        if self.attributeStore is None:
            self.attributeStore = self.loadAttributeStore()
        return DomainReqHandler(self.domainLedger,
                                self.states[DOMAIN_LEDGER_ID],
                                self.reqProcessors,
                                self.idrCache,
                                self.attributeStore
                                )

    def getIdrCache(self):
        return IdrCache(
            self.name,
            initKeyValueStorage(
                self.config.idrCacheStorage,
                self.dataLocation,
                self.config.idrCacheDbName)
        )

    def getConfigLedger(self):
        return Ledger(CompactMerkleTree(hashStore=FileHashStore(
            fileNamePrefix='config', dataDir=self.dataLocation)),
            dataDir=self.dataLocation,
            fileName=self.config.configTransactionsFile,
            ensureDurability=self.config.EnsureLedgerDurability)

    def loadConfigState(self):
        return PruningState(
            initKeyValueStorage(
                self.config.configStateStorage,
                self.dataLocation,
                self.config.configStateDbName)
        )

    def loadAttributeStore(self):
        return AttributeStore(
            initKeyValueStorage(
                self.config.attrStorage,
                self.dataLocation,
                self.config.attrDbName)
        )

    def getConfigReqHandler(self):
        return ConfigReqHandler(self.configLedger,
                                self.states[CONFIG_LEDGER_ID],
                                self.idrCache, self.upgrader,
                                self.poolManager)

    def initConfigState(self):
        self.initStateFromLedger(self.states[CONFIG_LEDGER_ID],
                                 self.configLedger, self.configReqHandler)

    def postDomainLedgerCaughtUp(self, **kwargs):
        super().postDomainLedgerCaughtUp(**kwargs)
        self.acknowledge_upgrade()

    def start_config_ledger_sync(self):
        self._sync_ledger(CONFIG_LEDGER_ID)
        self.ledgerManager.processStashedLedgerStatuses(CONFIG_LEDGER_ID)

    def post_txn_from_catchup_added_to_domain_ledger(self, txn):
        pass

    def sendConfigLedgerStatus(self, nodeName):
        self.sendLedgerStatus(nodeName, CONFIG_LEDGER_ID)

    @property
    def configLedgerStatus(self):
        return self.build_ledger_status(CONFIG_LEDGER_ID)

    def getLedgerStatus(self, ledgerId: int):
        if ledgerId == CONFIG_LEDGER_ID:
            return self.configLedgerStatus
        else:
            return super().getLedgerStatus(ledgerId)

    def postPoolLedgerCaughtUp(self, **kwargs):
        # The only reason to override this is to set the correct node id in
        # the upgrader since when the upgrader is initialized, node might not
        # have its id since it maybe missing the complete pool ledger.
        self.upgrader.nodeId = self.id
        super().postPoolLedgerCaughtUp(**kwargs)

    def catchup_next_ledger_after_pool(self):
        self.start_config_ledger_sync()

    def postConfigLedgerCaughtUp(self, **kwargs):
        self.upgrader.processLedger()
        self.start_domain_ledger_sync()

    def acknowledge_upgrade(self):
        if self.upgrader.isItFirstRunAfterUpgrade:
            logger.debug('{} found the first run after upgrade, will '
                         'send NODE_UPGRADE'.format(self))
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

    def postRecvTxnFromCatchup(self, ledgerId: int, txn: Any):
        if ledgerId == CONFIG_LEDGER_ID:
            # Since no config ledger transactions are applied to the state
            return None
        else:
            return super().postRecvTxnFromCatchup(ledgerId, txn)

    def validateNodeMsg(self, wrappedMsg):
        msg, frm = wrappedMsg
        if all(attr in msg.keys()
               for attr in [OPERATION, f.IDENTIFIER.nm, f.REQ_ID.nm]) \
                and msg.get(OPERATION, {}).get(TXN_TYPE) == NODE_UPGRADE:
            cls = self._client_request_class
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

    def processRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == GET_NYM:
            self.send_ack_to_client(request.key, frm)
            result = self.reqHandler.handleGetNymReq(request, frm)
            self.transmitToClient(Reply(result), frm)
        elif request.operation[TXN_TYPE] == GET_SCHEMA:
            self.send_ack_to_client(request.key, frm)
            # TODO: `handleGetSchemaReq` should be changed to
            # `get_reply_for_schema_req`, the rationale being that the method
            # is not completely handling the request but fetching a response.
            # Similar reasoning follows for other methods below
            result = self.reqHandler.handleGetSchemaReq(request, frm)
            self.transmitToClient(Reply(result), frm)
        elif request.operation[TXN_TYPE] == GET_ATTR:
            self.send_ack_to_client(request.key, frm)
            result = self.reqHandler.handleGetAttrsReq(request, frm)
            self.transmitToClient(Reply(result), frm)
        elif request.operation[TXN_TYPE] == GET_CLAIM_DEF:
            self.send_ack_to_client(request.key, frm)
            result = self.reqHandler.handleGetClaimDefReq(request, frm)
            self.transmitToClient(Reply(result), frm)
        else:
            # forced request should be processed before consensus
            if request.operation[TXN_TYPE] == POOL_UPGRADE and request.isForced():
                self.configReqHandler.validate(request)
                self.configReqHandler.applyForced(request)
            super().processRequest(request, frm)

    @classmethod
    def ledgerId(cls, txnType: str):
        # It was called ledgerTypeForTxn before
        if txnType in POOL_TXN_TYPES:
            return POOL_LEDGER_ID
        if txnType in IDENTITY_TXN_TYPES:
            return DOMAIN_LEDGER_ID
        if txnType in CONFIG_TXN_TYPES:
            return CONFIG_LEDGER_ID

    def applyReq(self, request: Request, cons_time):
        """
        Apply request to appropriate ledger and state
        """
        if self.__class__.ledgerIdForRequest(request) == CONFIG_LEDGER_ID:
            return self.configReqHandler.apply(request, cons_time)
        else:
            return super().applyReq(request, cons_time)

    def executeDomainTxns(self, ppTime, reqs: List[Request], stateRoot,
                          txnRoot) -> List:
        """
        Execute the REQUEST sent to this Node

        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST  
        """
        return self.commitAndSendReplies(self.reqHandler, ppTime, reqs,
                                         stateRoot, txnRoot)

    def executeConfigTxns(self, ppTime, reqs: List[Request], stateRoot,
                          txnRoot) -> List:
        return self.commitAndSendReplies(self.configReqHandler, ppTime, reqs,
                                         stateRoot, txnRoot)

    def update_txn_with_extra_data(self, txn):
        """
        All the data of the transaction might not be stored in ledger so the
        extra data that is omitted from ledger needs to be fetched from the
        appropriate data store
        :param txn:
        :return:
        """
        # For RAW and ENC attributes, only hash is stored in the ledger.
        if txn[TXN_TYPE] == ATTRIB:
            # The key needs to be present and not None
            key = RAW if (RAW in txn and txn[RAW] is not None) else \
                ENC if (ENC in txn and txn[ENC] is not None) else \
                None
            if key:
                txn[key] = self.attributeStore.get(txn[key])
        return txn

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

    def onBatchRejected(self, ledgerId):
        if ledgerId == CONFIG_LEDGER_ID:
            self.configReqHandler.onBatchRejected()
        else:
            super().onBatchRejected(ledgerId)
