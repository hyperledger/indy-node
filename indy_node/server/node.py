from datetime import timedelta

from typing import Iterable, List

from common.exceptions import LogicError
from indy_common.authorize.auth_constraints import AbstractConstraintSerializer
from indy_node.server.node_bootstrap import NodeBootstrap
from indy_node.server.txn_version_controller import TxnVersionController

from indy_node.server.validator_info_tool import ValidatorNodeInfoTool

from plenum.common.constants import VERSION, \
    ENC, RAW, CURRENT_PROTOCOL_VERSION, FORCE, ATTRIB_LABEL, IDR_CACHE_LABEL
from plenum.common.txn_util import get_type, get_payload_data, TxnUtilConfig
from plenum.common.types import f, \
    OPERATION
from plenum.common.util import get_utc_datetime
from plenum.server.node import Node as PlenumNode
from state.pruning_state import PruningState
from indy_common.config_util import getConfig
from indy_common.constants import TXN_TYPE, ATTRIB, DATA, ACTION, \
    NODE_UPGRADE, COMPLETE, FAIL, POOL_UPGRADE, POOL_CONFIG, \
    IN_PROGRESS, AUTH_RULE, AUTH_RULES
from indy_common.types import Request, SafeRequest
from indy_common.config_helper import NodeConfigHelper
from indy_node.server.client_authn import LedgerBasedAuthNr
from indy_node.server.node_authn import NodeAuthNr
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
                 config=None,
                 bootstrap_cls=NodeBootstrap):
        config = config or getConfig()

        config_helper = config_helper or NodeConfigHelper(name, config)

        ledger_dir = ledger_dir or config_helper.ledger_dir
        keys_dir = keys_dir or config_helper.keys_dir
        genesis_dir = genesis_dir or config_helper.genesis_dir
        plugins_dir = plugins_dir or config_helper.plugins_dir
        node_info_dir = node_info_dir or config_helper.node_info_dir

        # TODO: 4 ugly lines ahead, don't know how to avoid
        # self.idrCache = None
        # self.attributeStore = None
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
                         pluginPaths=pluginPaths,
                         storage=storage,
                         config=config,
                         bootstrap_cls=bootstrap_cls)

        # TODO: ugly line ahead, don't know how to avoid
        self.clientAuthNr = clientAuthNr or self.defaultAuthNr()

        self.nodeMsgRouter.routes[Request] = self.processNodeRequest
        self.nodeAuthNr = self.defaultNodeAuthNr()
        self.db_manager.set_txn_version_controller(TxnVersionController())

    @property
    def attributeStore(self):
        return self.db_manager.get_store(ATTRIB_LABEL)

    @property
    def idrCache(self):
        return self.db_manager.get_store(IDR_CACHE_LABEL)

    def on_inconsistent_3pc_state(self):
        timeout = self.config.INCONSISTENCY_WATCHER_NETWORK_TIMEOUT
        logger.warning("Suspecting inconsistent 3PC state, going to restart in {} seconds".format(timeout))

        now = get_utc_datetime()
        when = now + timedelta(seconds=timeout)
        self.restarter.requestRestart(when)

    def getIdrCache(self):
        return self.idrCache

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
        return LedgerBasedAuthNr(self.write_manager.txn_types,
                                 self.read_manager.txn_types,
                                 self.action_manager.txn_types,
                                 self.idrCache)

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
                                                         AUTH_RULE,
                                                         AUTH_RULES]

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
