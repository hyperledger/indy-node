from typing import List

from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.txn_util import reqToTxn, is_forced, get_payload_data, append_txn_metadata
from plenum.server.ledger_req_handler import LedgerRequestHandler
from plenum.common.constants import TXN_TYPE, NAME, VERSION, FORCE
from indy_common.constants import POOL_UPGRADE, START, CANCEL, SCHEDULE, ACTION, POOL_CONFIG, NODE_UPGRADE, PACKAGE, \
    APP_NAME, REINSTALL
from indy_common.types import Request
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.upgrader import Upgrader
from indy_node.server.pool_config import PoolConfig
from indy_node.utils.node_control_utils import NodeControlUtil


class ConfigReqHandler(LedgerRequestHandler):
    write_types = {POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG}

    def __init__(self, ledger, state, idrCache: IdrCache,
                 upgrader: Upgrader, poolManager, poolCfg: PoolConfig):
        super().__init__(ledger, state)
        self.idrCache = idrCache
        self.upgrader = upgrader
        self.poolManager = poolManager
        self.poolCfg = poolCfg
        self.write_req_validator = WriteRequestValidator(config=getConfig(),
                                                         auth_map=auth_map,
                                                         cache=self.idrCache,
                                                         anyone_can_write_map=anyone_can_write_map)

    def doStaticValidation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        if operation[TXN_TYPE] == POOL_UPGRADE:
            self._doStaticValidationPoolUpgrade(identifier, req_id, operation)
        elif operation[TXN_TYPE] == POOL_CONFIG:
            self._doStaticValidationPoolConfig(identifier, req_id, operation)

    def _doStaticValidationPoolConfig(self, identifier, reqId, operation):
        pass

    def _doStaticValidationPoolUpgrade(self, identifier, reqId, operation):
        action = operation.get(ACTION)
        if action not in (START, CANCEL):
            raise InvalidClientRequest(identifier, reqId,
                                       "{} not a valid action".
                                       format(action))
        if action == START:
            schedule = operation.get(SCHEDULE, {})
            force = operation.get(FORCE)
            force = str(force) == 'True'
            isValid, msg = self.upgrader.isScheduleValid(
                schedule, self.poolManager.getNodesServices(), force)
            if not isValid:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid schedule since {}".
                                           format(schedule, msg))

        # TODO: Check if cancel is submitted before start

    def curr_pkt_info(self, pkg_name):
        if pkg_name == APP_NAME:
            return Upgrader.getVersion(), [APP_NAME]
        return NodeControlUtil.curr_pkt_info(pkg_name)

    def validate(self, req: Request):
        status = '*'
        operation = req.operation
        typ = operation.get(TXN_TYPE)
        if typ not in [POOL_UPGRADE, POOL_CONFIG]:
            return
        if typ == POOL_UPGRADE:
            pkt_to_upgrade = req.operation.get(PACKAGE, getConfig().UPGRADE_ENTRY)
            if pkt_to_upgrade:
                currentVersion, cur_deps = self.curr_pkt_info(pkt_to_upgrade)
                if not currentVersion:
                    raise InvalidClientRequest(req.identifier, req.reqId,
                                               "Packet {} is not installed and cannot be upgraded".
                                               format(pkt_to_upgrade))
                if all([APP_NAME not in d for d in cur_deps]):
                    raise InvalidClientRequest(req.identifier, req.reqId,
                                               "Packet {} doesn't belong to pool".format(pkt_to_upgrade))
            else:
                raise InvalidClientRequest(req.identifier, req.reqId, "Upgrade packet name is empty")

            targetVersion = req.operation[VERSION]
            reinstall = req.operation.get(REINSTALL, False)
            if not Upgrader.is_version_upgradable(currentVersion, targetVersion, reinstall):
                # currentVersion > targetVersion
                raise InvalidClientRequest(req.identifier, req.reqId, "Version is not upgradable")

            action = operation.get(ACTION)
            # TODO: Some validation needed for making sure name and version
            # present
            txn = self.upgrader.get_upgrade_txn(
                lambda txn: get_payload_data(txn).get(
                    NAME,
                    None) == req.operation.get(
                    NAME,
                    None) and get_payload_data(txn).get(VERSION) == req.operation.get(VERSION),
                reverse=True)
            if txn:
                status = get_payload_data(txn).get(ACTION, '*')

            if status == START and action == START:
                raise InvalidClientRequest(
                    req.identifier,
                    req.reqId,
                    "Upgrade '{}' is already scheduled".format(
                        req.operation.get(NAME)))
            if status == '*':
                auth_action = AuthActionAdd(txn_type=POOL_UPGRADE,
                                            field=ACTION,
                                            value=action)
            else:
                auth_action = AuthActionEdit(txn_type=POOL_UPGRADE,
                                             field=ACTION,
                                             old_value=status,
                                             new_value=action)
            self.write_req_validator.validate(req,
                                              [auth_action])
        elif typ == POOL_CONFIG:
            action = '*'
            status = '*'
            self.write_req_validator.validate(req,
                                              [AuthActionEdit(txn_type=typ,
                                                              field=ACTION,
                                                              old_value=status,
                                                              new_value=action)])

    def apply(self, req: Request, cons_time):
        txn = append_txn_metadata(reqToTxn(req),
                                  txn_time=cons_time)
        self.ledger.append_txns_metadata([txn])
        (start, _), _ = self.ledger.appendTxns([txn])
        return start, txn

    def commit(self, txnCount, stateRoot, txnRoot, ppTime) -> List:
        committedTxns = super().commit(txnCount, stateRoot, txnRoot, ppTime)
        for txn in committedTxns:
            # Handle POOL_UPGRADE or POOL_CONFIG transaction here
            # only in case it is not forced.
            # If it is forced then it was handled earlier
            # in applyForced method.
            if not is_forced(txn):
                self.upgrader.handleUpgradeTxn(txn)
                self.poolCfg.handleConfigTxn(txn)
        return committedTxns

    def applyForced(self, req: Request):
        super().applyForced(req)
        txn = reqToTxn(req)
        self.upgrader.handleUpgradeTxn(txn)
        self.poolCfg.handleConfigTxn(txn)
