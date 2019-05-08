from datetime import timedelta

from typing import Iterable, List

from common.exceptions import LogicError
from common.serializers.serialization import ledger_txn_serializer, domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintsSerializer, AbstractConstraintSerializer
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_node.server.pool_req_handler import PoolRequestHandler

from indy_node.server.action_req_handler import ActionReqHandler
from indy_node.server.restarter import Restarter
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.genesis_txn.genesis_txn_initiator_from_file import GenesisTxnInitiatorFromFile
from indy_node.server.validator_info_tool import ValidatorNodeInfoTool

from plenum.common.constants import VERSION, NODE_PRIMARY_STORAGE_SUFFIX, \
    ENC, RAW, DOMAIN_LEDGER_ID, CURRENT_PROTOCOL_VERSION, FORCE, POOL_LEDGER_ID
from plenum.common.ledger import Ledger
from plenum.common.txn_util import get_type, get_payload_data, TxnUtilConfig
from plenum.common.types import f, \
    OPERATION
from plenum.common.util import get_utc_datetime
from plenum.persistence.storage import initStorage
from plenum.server.node import Node as PlenumNode
from state.pruning_state import PruningState
from storage.helper import initKeyValueStorage
from indy_common.config_util import getConfig
from indy_common.constants import TXN_TYPE, ATTRIB, DATA, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, CONFIG_LEDGER_ID, POOL_UPGRADE, POOL_CONFIG, \
    IN_PROGRESS, AUTH_RULE
from indy_common.types import Request, SafeRequest
from indy_common.config_helper import NodeConfigHelper
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.client_authn import LedgerBasedAuthNr
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.server.domain_req_handler import DomainReqHandler
from indy_node.server.node_authn import NodeAuthNr
from indy_node.server.upgrader import Upgrader
from indy_node.server.pool_config import PoolConfig
from stp_core.common.log import getlogger

logger = getlogger()


class Node(PlenumNode):
    keygenScript = "init_indy_keys"
    client_request_class = SafeRequest
    TxnUtilConfig.client_request_class = Request
    _info_tool_class = ValidatorNodeInfoTool

    def __init__(self,
                 name,
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
                 pluginPaths: Iterable[str] = None,
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
        self.restarter = None
        self.poolCfg = None

        super().__init__(name=name,
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

        self.upgrader = self.init_upgrader()
        self.restarter = self.init_restarter()
        self.poolCfg = self.init_pool_config()

        # TODO: ugly line ahead, don't know how to avoid
        self.clientAuthNr = clientAuthNr or self.defaultAuthNr()

        self.nodeMsgRouter.routes[Request] = self.processNodeRequest
        self.nodeAuthNr = self.defaultNodeAuthNr()

        # Will be refactored soon
        self.get_req_handler(CONFIG_LEDGER_ID).upgrader = self.upgrader
        self.get_req_handler(CONFIG_LEDGER_ID).poolCfg = self.poolCfg
        self.actionReqHandler.poolCfg = self.poolCfg
        self.actionReqHandler.restarter = self.restarter

    def init_pool_config(self):
        return PoolConfig(self.configLedger)

    def on_inconsistent_3pc_state(self):
        timeout = self.config.INCONSISTENCY_WATCHER_NETWORK_TIMEOUT
        logger.warning("Suspecting inconsistent 3PC state, going to restart in {} seconds".format(timeout))

        now = get_utc_datetime()
        when = now + timedelta(seconds=timeout)
        self.restarter.requestRestart(when)

    def init_domain_ledger(self):
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

    def init_upgrader(self):
        return Upgrader(self.id,
                        self.name,
                        self.dataLocation,
                        self.config,
                        self.configLedger,
                        actionFailedCallback=self.postConfigLedgerCaughtUp,
                        action_start_callback=self.notify_upgrade_start)

    def init_restarter(self):
        return Restarter(self.id,
                         self.name,
                         self.dataLocation,
                         self.config)

    def init_pool_req_handler(self):
        return PoolRequestHandler(self.poolLedger,
                                  self.states[POOL_LEDGER_ID],
                                  self.states,
                                  self.getIdrCache(),
                                  self.write_req_validator)

    def init_domain_req_handler(self):
        if self.attributeStore is None:
            self.attributeStore = self.init_attribute_store()
        return DomainReqHandler(self.domainLedger,
                                self.states[DOMAIN_LEDGER_ID],
                                self.config,
                                self.reqProcessors,
                                self.getIdrCache(),
                                self.attributeStore,
                                self.bls_bft.bls_store,
                                self.write_req_validator,
                                self.getStateTsDbStorage())

    def init_config_req_handler(self):
        return ConfigReqHandler(self.configLedger,
                                self.states[CONFIG_LEDGER_ID],
                                self.getIdrCache(),
                                self.upgrader,
                                self.poolManager,
                                self.poolCfg,
                                self.write_req_validator,
                                self.bls_bft.bls_store,
                                self.getStateTsDbStorage())

    def getIdrCache(self):
        if self.idrCache is None:
            self.idrCache = IdrCache(self.name,
                                     initKeyValueStorage(self.config.idrCacheStorage,
                                                         self.dataLocation,
                                                         self.config.idrCacheDbName,
                                                         db_config=self.config.db_idr_cache_db_config)
                                     )
        return self.idrCache

    def init_attribute_store(self):
        return AttributeStore(
            initKeyValueStorage(
                self.config.attrStorage,
                self.dataLocation,
                self.config.attrDbName,
                db_config=self.config.db_attr_db_config)
        )

    def init_action_req_handler(self):
        return ActionReqHandler(self.getIdrCache(),
                                self.restarter,
                                self.poolManager,
                                self.poolCfg,
                                self._info_tool,
                                self.write_req_validator)

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

    def preLedgerCatchUp(self, ledger_id):
        super().preLedgerCatchUp(ledger_id)

        if len(self.idrCache.un_committed) > 0:
            raise LogicError('{} idr cache has uncommitted txns before catching up ledger {}'.format(self, ledger_id))

    def postLedgerCatchUp(self, ledger_id):
        if len(self.idrCache.un_committed) > 0:
            raise LogicError('{} idr cache has uncommitted txns after catching up ledger {}'.format(self, ledger_id))

        super().postLedgerCatchUp(ledger_id)

    def acknowledge_upgrade(self):
        if not self.upgrader.should_notify_about_upgrade_result():
            return
        lastUpgradeVersion = self.upgrader.lastActionEventInfo.data.version
        action = COMPLETE if self.upgrader.didLastExecutedUpgradeSucceeded else FAIL
        logger.info('{} found the first run after upgrade, sending NODE_UPGRADE {} to version {}'.format(
            self, action, lastUpgradeVersion))
        op = {
            TXN_TYPE: NODE_UPGRADE,
            DATA: {
                ACTION: action,
                VERSION: lastUpgradeVersion.full
            }
        }
        op[f.SIG.nm] = self.wallet.signMsg(op[DATA])

        request = self.wallet.signRequest(
            Request(operation=op, protocolVersion=CURRENT_PROTOCOL_VERSION))

        self.startedProcessingReq(request.key, self.nodestack.name)
        self.send(request)
        self.upgrader.notified_about_action_result()

    def notify_upgrade_start(self):
        scheduled_upgrade_version = self.upgrader.scheduledAction.version
        action = IN_PROGRESS
        logger.info('{} is about to be upgraded, '
                    'sending NODE_UPGRADE {} to version {}'.format(self, action, scheduled_upgrade_version))
        op = {
            TXN_TYPE: NODE_UPGRADE,
            DATA: {
                ACTION: action,
                VERSION: scheduled_upgrade_version.full
            }
        }
        op[f.SIG.nm] = self.wallet.signMsg(op[DATA])

        # do not send protocol version before all Nodes support it after Upgrade
        request = self.wallet.signRequest(
            Request(operation=op, protocolVersion=CURRENT_PROTOCOL_VERSION))

        self.startedProcessingReq(request.key,
                                  self.nodestack.name)
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
        if not self.isProcessingReq(request.key):
            self.startedProcessingReq(request.key, frm)
        # If not already got the propagate request(PROPAGATE) for the
        # corresponding client request(REQUEST)
        self.recordAndPropagate(request, frm)

    def validateNodeMsg(self, wrappedMsg):
        msg, frm = wrappedMsg
        if all(attr in msg.keys()
               for attr in [OPERATION, f.IDENTIFIER.nm, f.REQ_ID.nm]) \
                and msg.get(OPERATION, {}).get(TXN_TYPE) == NODE_UPGRADE:
            cls = self.client_request_class
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
        c += self.restarter.service()
        return c

    def can_write_txn(self, txn_type):
        return self.poolCfg.isWritable() or txn_type in [POOL_UPGRADE,
                                                         POOL_CONFIG,
                                                         AUTH_RULE]

    def execute_domain_txns(self, three_pc_batch) -> List:
        """
        Execute the REQUEST sent to this Node

        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST
        """
        return self.default_executer(three_pc_batch)

    def update_txn_with_extra_data(self, txn):
        """
        All the data of the transaction might not be stored in ledger so the
        extra data that is omitted from ledger needs to be fetched from the
        appropriate data store
        :param txn:
        :return:
        """
        # For RAW and ENC attributes, only hash is stored in the ledger.
        if get_type(txn) == ATTRIB:
            txn_data = get_payload_data(txn)
            # The key needs to be present and not None
            key = RAW if (RAW in txn_data and txn_data[RAW] is not None) else \
                ENC if (ENC in txn_data and txn_data[ENC] is not None) else None
            if key:
                txn_data[key] = self.attributeStore.get(txn_data[key])
        return txn

    def closeAllKVStores(self):
        super().closeAllKVStores()
        if self.idrCache:
            self.idrCache.close()
        if self.attributeStore:
            self.attributeStore.close()

    def is_request_need_quorum(self, msg_dict: dict):
        txn_type = msg_dict.get(OPERATION).get(TXN_TYPE, None) \
            if OPERATION in msg_dict \
            else None
        is_force = OPERATION in msg_dict and msg_dict.get(OPERATION).get(FORCE, False)
        is_force_upgrade = str(is_force) == 'True' and txn_type == POOL_UPGRADE
        return txn_type and not is_force_upgrade and super().is_request_need_quorum(msg_dict)

    @staticmethod
    def add_auth_rules_to_config_state(state: PruningState,
                                       auth_map: dict,
                                       serializer: AbstractConstraintSerializer):
        for rule_id, auth_constraint in auth_map.items():
            serialized_key = rule_id.encode()
            serialized_value = serializer.serialize(auth_constraint)
            if not state.get(serialized_key, isCommitted=False):
                state.set(serialized_key, serialized_value)

    def _init_write_request_validator(self):
        constraint_serializer = ConstraintsSerializer(domain_state_serializer)
        config_state = self.states[CONFIG_LEDGER_ID]
        self.write_req_validator = WriteRequestValidator(config=self.config,
                                                         auth_map=auth_map,
                                                         cache=self.getIdrCache(),
                                                         config_state=config_state,
                                                         state_serializer=constraint_serializer,
                                                         anyone_can_write_map=anyone_can_write_map,
                                                         metrics=self.metrics)
