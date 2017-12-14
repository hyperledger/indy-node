from typing import Iterable, Any, List

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.genesis_txn.genesis_txn_initiator_from_file import GenesisTxnInitiatorFromFile
from indy_node.server.validator_info_tool import ValidatorNodeInfoTool

from plenum.common.constants import VERSION, NODE_PRIMARY_STORAGE_SUFFIX, \
    ENC, RAW, DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.ledger import Ledger
from plenum.common.types import f, \
    OPERATION
from plenum.persistence.storage import initStorage, initKeyValueStorage
from plenum.server.node import Node as PlenumNode
from indy_common.config_util import getConfig
from indy_common.constants import TXN_TYPE, ATTRIB, DATA, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, CONFIG_LEDGER_ID, POOL_UPGRADE, POOL_CONFIG,\
    IN_PROGRESS
from indy_common.types import Request, SafeRequest
from indy_common.config_helper import NodeConfigHelper
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.client_authn import LedgerBasedAuthNr
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.server.domain_req_handler import DomainReqHandler
from indy_node.server.node_authn import NodeAuthNr
from indy_node.server.pool_manager import HasPoolManager
from indy_node.server.upgrader import Upgrader
from indy_node.server.pool_config import PoolConfig
from stp_core.common.log import getlogger


logger = getlogger()


class Node(PlenumNode, HasPoolManager):
    keygenScript = "init_indy_keys"
    _client_request_class = SafeRequest
    _info_tool_class = ValidatorNodeInfoTool

    def __init__(self,
                 name,
                 nodeRegistry=None,
                 clientAuthNr=None,
                 ha=None,
                 cliname=None,
                 cliha=None,
                 config_helper=None,
                 ledger_dir: str = None,
                 keys_dir: str = None,
                 genesis_dir: str = None,
                 plugins_dir: str = None,
                 node_info_dir: str = None,
                 primaryDecider=None,
                 pluginPaths: Iterable[str]=None,
                 storage=None,
                 config=None):
        config = config or getConfig()

        config_helper = config_helper or NodeConfigHelper(name, config)

        ledger_dir = ledger_dir or config_helper.ledger_dir
        keys_dir = keys_dir or config_helper.keys_dir
        genesis_dir = genesis_dir or config_helper.genesis_dir
        plugins_dir = plugins_dir or config_helper.plugins_dir
        node_info_dir = node_info_dir or config_helper.node_info_dir

        # TODO: 4 ugly lines ahead, don't know how to avoid
        self.idrCache = None
        self.attributeStore = None
        self.upgrader = None
        self.poolCfg = None

        super().__init__(name=name,
                         nodeRegistry=nodeRegistry,
                         clientAuthNr=clientAuthNr,
                         ha=ha,
                         cliname=cliname,
                         cliha=cliha,
                         config_helper=config_helper,
                         ledger_dir=ledger_dir,
                         keys_dir=keys_dir,
                         genesis_dir=genesis_dir,
                         plugins_dir=plugins_dir,
                         node_info_dir=node_info_dir,
                         primaryDecider=primaryDecider,
                         pluginPaths=pluginPaths,
                         storage=storage,
                         config=config)

        # TODO: ugly line ahead, don't know how to avoid
        self.clientAuthNr = clientAuthNr or self.defaultAuthNr()

        self.nodeMsgRouter.routes[Request] = self.processNodeRequest
        self.nodeAuthNr = self.defaultNodeAuthNr()

    def getPoolConfig(self):
        return PoolConfig(self.configLedger)

    def initPoolManager(self, nodeRegistry, ha, cliname, cliha):
        HasPoolManager.__init__(self, nodeRegistry, ha, cliname, cliha)

    def getPrimaryStorage(self):
        """
        This is usually an implementation of Ledger
        """
        if self.config.primaryStorage is None:
            genesis_txn_initiator = GenesisTxnInitiatorFromFile(
                self.genesis_dir, self.config.domainTransactionsFile)
            return Ledger(
                CompactMerkleTree(
                    hashStore=self.getHashStore('domain')),
                dataDir=self.dataLocation,
                fileName=self.config.domainTransactionsFile,
                ensureDurability=self.config.EnsureLedgerDurability,
                genesis_txn_initiator=genesis_txn_initiator)
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
                        upgradeFailedCallback=self.postConfigLedgerCaughtUp,
                        upgrade_start_callback=self.notify_upgrade_start)

    def getDomainReqHandler(self):
        if self.attributeStore is None:
            self.attributeStore = self.loadAttributeStore()
        return DomainReqHandler(self.domainLedger,
                                self.states[DOMAIN_LEDGER_ID],
                                self.config,
                                self.reqProcessors,
                                self.getIdrCache(),
                                self.attributeStore,
                                self.bls_bft.bls_store)

    def getIdrCache(self):
        if self.idrCache is None:
            self.idrCache = IdrCache(self.name,
                                     initKeyValueStorage(self.config.idrCacheStorage,
                                                         self.dataLocation,
                                                         self.config.idrCacheDbName)
                                     )
        return self.idrCache

    def loadAttributeStore(self):
        return AttributeStore(
            initKeyValueStorage(
                self.config.attrStorage,
                self.dataLocation,
                self.config.attrDbName)
        )

    def setup_config_req_handler(self):
        self.upgrader = self.getUpgrader()
        self.poolCfg = self.getPoolConfig()
        super().setup_config_req_handler()

    def getConfigReqHandler(self):
        return ConfigReqHandler(self.configLedger,
                                self.states[CONFIG_LEDGER_ID],
                                self.getIdrCache(),
                                self.upgrader,
                                self.poolManager,
                                self.poolCfg)

    def post_txn_from_catchup_added_to_domain_ledger(self, txn):
        pass

    def postPoolLedgerCaughtUp(self, **kwargs):
        # The only reason to override this is to set the correct node id in
        # the upgrader since when the upgrader is initialized, node might not
        # have its id since it maybe missing the complete pool ledger.
        self.upgrader.nodeId = self.id
        super().postPoolLedgerCaughtUp(**kwargs)

    def postConfigLedgerCaughtUp(self, **kwargs):
        self.poolCfg.processLedger()
        self.upgrader.processLedger()
        super().postConfigLedgerCaughtUp(**kwargs)
        self.acknowledge_upgrade()

    def acknowledge_upgrade(self):
        if not self.upgrader.should_notify_about_upgrade_result():
            return
        lastUpgradeVersion = self.upgrader.lastUpgradeEventInfo[2]
        action = COMPLETE if self.upgrader.didLastExecutedUpgradeSucceeded else FAIL
        logger.info('{} found the first run after upgrade, sending NODE_UPGRADE {} to version {}'.format(
            self, action, lastUpgradeVersion))
        op = {
            TXN_TYPE: NODE_UPGRADE,
            DATA: {
                ACTION: action,
                VERSION: lastUpgradeVersion
            }
        }
        op[f.SIG.nm] = self.wallet.signMsg(op[DATA])

        # do not send protocol version before all Nodes support it after Upgrade
        request = self.wallet.signRequest(
            Request(operation=op, protocolVersion=None))

        self.startedProcessingReq(*request.key, self.nodestack.name)
        self.send(request)
        self.upgrader.notified_about_upgrade_result()

    def notify_upgrade_start(self):
        scheduled_upgrade_version = self.upgrader.scheduledUpgrade[0]
        action = IN_PROGRESS
        logger.info('{} is about to be upgraded, '
                    'sending NODE_UPGRADE {} to version {}'.format(self, action, scheduled_upgrade_version))
        op = {
            TXN_TYPE: NODE_UPGRADE,
            DATA: {
                ACTION: action,
                VERSION: scheduled_upgrade_version
            }
        }
        op[f.SIG.nm] = self.wallet.signMsg(op[DATA])

        # do not send protocol version before all Nodes support it after Upgrade
        request = self.wallet.signRequest(
            Request(operation=op, protocolVersion=None))

        self.startedProcessingReq(*request.key, self.nodestack.name)
        self.send(request)

    def processNodeRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == NODE_UPGRADE:
            try:
                self.nodeAuthNr.authenticate(request.operation[DATA],
                                             request.identifier,
                                             request.operation[f.SIG.nm])
            except BaseException as ex:
                logger.warning('The request {} failed to authenticate {}'
                               .format(request, repr(ex)))
                return
        if not self.isProcessingReq(*request.key):
            self.startedProcessingReq(*request.key, frm)
        # If not already got the propagate request(PROPAGATE) for the
        # corresponding client request(REQUEST)
        self.recordAndPropagate(request, frm)

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

    def init_core_authenticator(self):
        return LedgerBasedAuthNr(self.idrCache)

    def defaultNodeAuthNr(self):
        return NodeAuthNr(self.poolLedger)

    async def prod(self, limit: int = None) -> int:
        c = await super().prod(limit)
        c += self.upgrader.service()
        return c

    def processRequest(self, request: Request, frm: str):
        if self.is_query(request.operation[TXN_TYPE]):
            self.process_query(request, frm)
            self.total_read_request_number += 1
        else:
            # forced request should be processed before consensus
            if (request.operation[TXN_TYPE] in [
                    POOL_UPGRADE, POOL_CONFIG]) and request.isForced():
                self.configReqHandler.validate(request)
                self.configReqHandler.applyForced(request)
            # here we should have write transactions that should be processed
            # only on writable pool
            if self.poolCfg.isWritable() or (request.operation[TXN_TYPE] in [
                    POOL_UPGRADE, POOL_CONFIG]):
                super().processRequest(request, frm)
            else:
                raise InvalidClientRequest(
                    request.identifier,
                    request.reqId,
                    'Pool is in readonly mode, try again in 60 seconds')

    def executeDomainTxns(self, ppTime, reqs: List[Request], stateRoot,
                          txnRoot) -> List:
        """
        Execute the REQUEST sent to this Node

        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST
        """
        return self.default_executer(DOMAIN_LEDGER_ID, ppTime, reqs,
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
